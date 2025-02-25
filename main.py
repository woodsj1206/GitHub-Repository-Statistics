"""
Program Name: GitHub Repository Statistics
Author: woodsj1206 (https://github.com/woodsj1206)
Description: This program uses GitHub's API to analyze stars, clones, forks, watchers, and traffic trends across a user's public repositories. 
Date Created: 2/18/25
Last Modified: 2/24/25
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
        api_handler (GitHubAPIHandler): An instance of GitHubAPIHandler for handling API requests.
        visibility (str, optional): Visibility of repositories to fetch (e.g., "public", "private").
                                    Defaults to "public".
                                        
    Returns:
        list: A list of repository dictionaries that match the specified visibility and belong to the user.
                Returns an empty list if no repositories match or if the API response is None.
    """
    
    github_repos_url = "https://api.github.com/user/repos"
        
    response = await api_handler.get_response_json(github_repos_url)
        
    # Filter repositories based on visibility and ownership
    repositories = [
        repo for repo in response 
            if repo["visibility"] == visibility and repo["owner"]["login"] == github_user.user_name
        ] if response else []
        
    return repositories
    

async def process_repository(api_handler: api_utils.GitHubAPIHandler, repository: dict, github_user: user.User, metric_tracker: repository_metric.RepositoryMetricsTracker, semaphore: asyncio.Semaphore, lock: asyncio.Lock):
    """
    Processes a GitHub repository's metrics and traffic data, tracking repository-level and traffic-related metrics.

    Args:
        api_handler (api_utils.GitHubAPIHandler): An instance of the API handler responsible for making API calls to GitHub.
        repository (dict): A dictionary containing repository data, including its name and metrics like stargazers, watchers, and forks.
        github_user (user.User): The GitHub user associated with the repository. Used to fetch user-specific API data.
        metric_tracker (repository_metric.RepositoryMetricsTracker): An instance of the metric tracker that collects and stores various repository metrics.

    The function performs the following:
    - Tracks basic repository metrics: stargazers, watchers, and forks.
    - Fetches traffic data from GitHub's API (views and clones) for the repository.
    - Tracks traffic-related metrics: total views, unique visitors, total clones, and unique cloners.

    Returns:
        None
    """    
    async with semaphore:
        repository_name = repository.get("name")
        print(f"\nRepository: {repository_name}...\n")

        # Construct the GitHub API URL for view and clone data of the current repository
        view_json, clones_json = await asyncio.gather(
            api_handler.get_response_json(f"https://api.github.com/repos/{github_user.user_name}/{repository_name}/traffic/views"),
            api_handler.get_response_json(f"https://api.github.com/repos/{github_user.user_name}/{repository_name}/traffic/clones")
        )
    
        async with lock:
            # Track basic repository metrics: stargazers, watchers, and forks
            metric_tracker.stargazers.add_repository_metric(repository_name, repository.get(metric_tracker.stargazers.name, 0))
            metric_tracker.watchers.add_repository_metric(repository_name, repository.get(metric_tracker.watchers.name, 0))
            metric_tracker.forks.add_repository_metric(repository_name, repository.get(metric_tracker.forks.name, 0))

            # Track traffic-related metrics: views and clones (both total and unique)
            metric_tracker.views.add_repository_traffic_metric(repository_name, view_json)
            metric_tracker.unique_vistors.add_repository_traffic_metric(repository_name, view_json)

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
    
    semaphore = asyncio.Semaphore(5)
    lock = asyncio.Lock()
    
    # Create a list of task for processing each repository
    tasks = [
        process_repository(api_handler, repository, github_user, metric_tracker, semaphore, lock) 
        for repository in repositories
        ]
    
    await asyncio.gather(*tasks)

    metric_tracker.print_metrics()
    
    # Generate an HTML content for the repository metrics
    repo_metrics_html_generator = html_generator.GitHubRepoMetricsHTMLGenerator(github_user.user_name, "dark")
    repo_metrics_html_generator.generate_html_for_metrics(metric_tracker)
    repo_metrics_html_generator.create_html_file("dark.html")
    
    # Generate an CSV report for the repository metrics
    csv_generator = CSVReportGenerator()
    csv_generator.generate_repository_metrics_report(metric_tracker)
    csv_generator.generate_traffic_metric_timestamp_report(metric_tracker.views)
    csv_generator.generate_traffic_metric_timestamp_report(metric_tracker.unique_vistors)
    csv_generator.generate_traffic_metric_timestamp_report(metric_tracker.clones)
    csv_generator.generate_traffic_metric_timestamp_report(metric_tracker.unique_cloners)
    csv_generator.generate_total_traffic_metrics_report(metric_tracker)
    

if __name__ == "__main__":
    asyncio.run(main())