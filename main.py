"""
Program Name: GitHub Repository Statistics
Author: woodsj1206 (https://github.com/woodsj1206)
Description: This program uses GitHub's API to analyze stars, clones, forks, watchers, and traffic trends across a user's public repositories. 
Date Created: 2/18/25
Last Modified: 3/11/25
"""

import asyncio
import os
import api_utils
import repository_metric
import html_generator
import user
from dotenv import find_dotenv, load_dotenv
from csv_report_generator import CSVReportGenerator


async def get_repositories(github_user: user.User, api_handler: api_utils.GitHubAPIHandler, visibility="public") -> list:
    """
    Retrieves the repositories owned by the user based on the specified visibility.
         
    Args:
        github_user (user.User): An instance of User for representing a GitHub user.
        api_handler (api_utils.GitHubAPIHandler): An instance of GitHubAPIHandler for handling API requests.
        visibility (str, optional): Visibility of repositories to fetch (e.g., "public", "private").
                                    Defaults to "public".
                                        
    Returns:
        list: A list of repository dictionaries that match the specified visibility and belong to the user.
                Returns an empty list if no repositories match or if the API response is None.
    """
    
    github_repos_url = f"https://api.github.com/user/repos?per_page=100&visibility={visibility}"
    
    user_repositories = []
    while github_repos_url:
        response = await api_handler.get_response(github_repos_url)
        
        response_json = response.json() if response else {}
        
        user_repositories.extend(response_json)
        
        link_header = response.headers.get("Link") if response else None
        
        if link_header:
            # Find the 'next' link in the header
            urls = link_header.split(',')
            next_url = None
            for url in urls:
                if 'rel="next"' in url:
                    # Extract the URL for the next page
                    next_url = url.split(';')[0].strip('<> ')
                    break
            
            # If there is a next page, update the URL for the next request
            github_repos_url = next_url
        else:
            # No more pages
            github_repos_url = None

        
    # Filter repositories based on visibility and ownership
    filtered_repositories = [
        repo for repo in user_repositories 
            if repo["owner"]["login"] == github_user.user_name
        ]
        
    return filtered_repositories
    

async def process_repository(api_handler: api_utils.GitHubAPIHandler, repository: dict, github_user: user.User, metric_tracker: repository_metric.RepositoryMetricsTracker, semaphore: asyncio.Semaphore, lock: asyncio.Lock) -> None:
    """
    Asynchronously processes and collects various metrics for a GitHub repository, including repository-level data and traffic analytics.

    Args:
        api_handler (api_utils.GitHubAPIHandler): The API handler used to interact with GitHub, fetching repository and traffic data.
        repository (dict): A dictionary containing repository details such as name, stargazers, watchers, and forks.
        github_user (user.User): A GitHub user object representing the repository's owner, used for fetching user-specific API data.
        metric_tracker (repository_metric.RepositoryMetricsTracker): An object that tracks and records repository metrics over time.
        semaphore (asyncio.Semaphore): A semaphore that limits concurrent API calls, helping manage rate limits and ensure efficient resource use.
        lock (asyncio.Lock): A lock used to ensure thread-safety when updating shared resources or states.

    Function Behavior:
        - Tracks basic repository metrics such as the number of stargazers, watchers, and forks.
        - Fetches traffic data from the GitHub API, including views and clones of the repository.
        - Records traffic-related metrics like total views, unique visitors, total clones, and unique cloners for analysis.

    Returns:
        None.
    """
    
    async with semaphore:
        repository_name = repository.get("name")
        print(f"\nRepository: {repository_name}...\n")

        # Construct the GitHub API URL for view and clone data of the current repository
        views_response, clones_repsonse = await asyncio.gather(
            api_handler.get_response(f"https://api.github.com/repos/{github_user.user_name}/{repository_name}/traffic/views"),
            api_handler.get_response(f"https://api.github.com/repos/{github_user.user_name}/{repository_name}/traffic/clones")
        )
        
        views_json = views_response.json() if views_response else {}
        clones_json = clones_repsonse.json() if clones_repsonse else {}

        async with lock:
            # Track basic repository metrics: stargazers, watchers, and forks
            metric_tracker.stargazers.add_repository_metric(repository_name, repository.get(metric_tracker.stargazers.name, 0))
            metric_tracker.watchers.add_repository_metric(repository_name, repository.get(metric_tracker.watchers.name, 0))
            metric_tracker.forks.add_repository_metric(repository_name, repository.get(metric_tracker.forks.name, 0))

            # Track traffic-related metrics: views and clones (both total and unique)
            metric_tracker.views.add_repository_traffic_metric(repository_name, views_json)
            metric_tracker.unique_vistors.add_repository_traffic_metric(repository_name, views_json)

            metric_tracker.clones.add_repository_traffic_metric(repository_name, clones_json)
            metric_tracker.unique_cloners.add_repository_traffic_metric(repository_name, clones_json)
    
        
async def main():
    # Locate the .env file and load environment variables
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)

    # Create a User instance with credentials from environment variables
    github_user = user.User(
        os.getenv("GITHUB_USERNAME"),
        os.getenv("PERSONAL_ACCESS_TOKEN")
    )

    # Initialize the GitHub API handler with the user's personal access token
    api_handler = api_utils.GitHubAPIHandler(github_user.personal_access_token)

    # Create an instance to track multiple repository metrics
    metric_tracker = repository_metric.RepositoryMetricsTracker()

    # Retrieve repositories owned by the GitHub user
    repositories = await get_repositories(github_user, api_handler)
    
    semaphore = asyncio.Semaphore(3)
    lock = asyncio.Lock()
    
    # Create a list of task for processing each repository
    tasks = [
        process_repository(api_handler, repository, github_user, metric_tracker, semaphore, lock) 
        for repository in repositories
        ]
    
    await asyncio.gather(*tasks)

    metric_tracker.print_metrics()
    
    # Ensure the folder exists
    output_folder = "output_files"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    # Generate an HTML content for the repository metrics
    repo_metrics_html_generator = html_generator.GitHubRepoMetricsHTMLGenerator(github_user.user_name, "light")
    repo_metrics_html_generator.generate_html_for_metrics(metric_tracker)
    repo_metrics_html_generator.create_html_file("index.html", output_folder)
    
    # Generate an CSV report for the repository metrics
    csv_generator = CSVReportGenerator()
    csv_generator.generate_repository_metrics_report(metric_tracker, output_folder)
    csv_generator.generate_traffic_metric_timestamp_report(metric_tracker.views, output_folder)
    csv_generator.generate_traffic_metric_timestamp_report(metric_tracker.unique_vistors, output_folder)
    csv_generator.generate_traffic_metric_timestamp_report(metric_tracker.clones, output_folder)
    csv_generator.generate_traffic_metric_timestamp_report(metric_tracker.unique_cloners, output_folder)
    csv_generator.generate_total_traffic_metrics_report(metric_tracker, output_folder)
    

if __name__ == "__main__":
    asyncio.run(main())