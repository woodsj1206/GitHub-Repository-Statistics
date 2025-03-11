from datetime import datetime, timedelta, timezone

class RepositoryMetric:
    """
    Tracks a specific metric (e.g., stars, views, forks) across multiple repositories.

    Attributes:
        name (str): The name of the metric being tracked.
        total_metric_count (int): Total sum of the metric across all repositories.
        max_metric_count (int): Highest recorded metric value among all repositories.
        repos_grouped_by_metric (dict): Maps metric counts to lists of repository names.
    """


    def __init__(self, name: str):
        """
        Initializes the RepositoryMetric instance with the specified metric name.

        Args:
            name (str): The metric name to track (e.g., 'stargazers_count').
        """
        
        self.name = name
        self.total_metric_count = 0
        self.max_metric_count = 0
        self.repos_grouped_by_metric = {}


    def add_repository_metric(self, repository_name: str, metric_count: int) -> None:
        """
        Adds the metric value for a given repository, updating total counts and grouping.

        Args:
            repository_name (str): The name of the repository.
            metric_count (int): The metric value for the repository.
            
        Returns:
            None.
        """
        
        self.total_metric_count += metric_count
        self.max_metric_count = max(self.max_metric_count, metric_count)
        self.repos_grouped_by_metric.setdefault(metric_count, []).append(repository_name)
     

    def get_top_repositories(self) -> list:
        """
        Retrieves repositories with the highest metric count.

        Returns:
            list: List of repository names with the highest metric count.
        """
        
        return self.repos_grouped_by_metric.get(self.max_metric_count, [])
    

    def print_metrics(self) -> None:
        """
        Prints the values of the attributes.
        
        Returns:
            None.
        """

        print(f"Metric Name: {self.name}")
        print(f"Total Metric Count: {self.total_metric_count}")
        print(f"Max Metric Count: {self.max_metric_count}")
        print(f"Repositories Grouped by Metric: {self.repos_grouped_by_metric}")



class RepositoryTrafficMetric(RepositoryMetric):
    """
    Extends RepositoryMetric to track time-based metrics (e.g., views, clones) across repositories.

    Attributes:
        metric_type (str): The type of traffic metric (e.g., 'views', 'clones').
        name (str): Specific metric attribute (e.g., 'count', 'uniques').
        total_metric_at_timestamps (dict): Tracks total metric counts per timestamp across all repositories.
    """
    

    def __init__(self, metric_type: str, name: str):
        """
        Initializes the RepositoryTrafficMetric instance.

        Args:
            metric_type (str): Type of traffic metric ('views' or 'clones').
            name (str): Specific metric attribute (e.g., 'count', 'uniques').
        """
        
        self.metric_type = metric_type
        super().__init__(name)
        self.total_metric_at_timestamps = self.generate_past_dates()


    def add_repository_traffic_metric(self, repository_name: str, metric_data: dict) -> None:
        """
        Processes and tracks traffic metric data (views or clones) for a given repository.

        Args:
            repository_name (str): The name of the repository for which the metric data is processed.
            metric_data (dict): A dictionary containing traffic data retrieved from the GitHub API.
                                Expected to have a key matching 'metric_type' (e.g., 'views', 'clones'),
                                with each entry containing a 'timestamp' and metric count.
                                
        Returns:
            None.
        """
        
        total_metric_count = 0
            
        for metric in metric_data.get(self.metric_type, []):
            metric_count = metric.get(self.name, 0)
            metric_timestamp = metric.get("timestamp")
            total_metric_count += metric_count

            self.total_metric_at_timestamps.setdefault(metric_timestamp, [0, []]) 
            self.total_metric_at_timestamps[metric_timestamp][0] += metric_count
            self.total_metric_at_timestamps[metric_timestamp][1].append((repository_name, metric_count))

        super().add_repository_metric(repository_name, total_metric_count)


    def generate_past_dates(self, days_back=14) -> dict[int, list]:
        """
        Generates a dictionary of ISO 8601 formatted dates (UTC) for the past specified number of days.

        Each date is mapped to a default list containing a zero value and an empty list.

        Args:
            days_back (int, optional): The number of days to go back from today (Defaults to 14).

        Returns:
            dict: A dictionary where each key is a date in 'YYYY-MM-DDT00:00:00Z' format (UTC),
                  and each value is a list containing a default zero value.
        """
        
        past_date_utc = datetime.now(timezone.utc).date() - timedelta(days=days_back) 
        return {
            f"{(past_date_utc + timedelta(days=day_offset))}T00:00:00Z": [0, []]
            for day_offset in range(days_back)
        }
    

    def print_metrics(self) -> None:
        """
        Prints the values of the attributes.

        Returns:
            None.
        """
        
        print(f"Metric Type: {self.metric_type}")
        super().print_metrics()
        print(f"Total Metric at Timestamps: {self.total_metric_at_timestamps}")



class RepositoryMetricsTracker:
    """
    Aggregates multiple RepositoryMetric and RepositoryTrafficMetric instances to track
    various repository statistics.

    Attributes:
        stargazers, watchers, forks (RepositoryMetric): Basic repository engagement metrics.
        views, unique_visitors, clones, unique_cloners (RepositoryTrafficMetric): Time-based traffic metrics.
    """
    

    def __init__(self):
        """Initializes all metric trackers for a repository."""

        self.stargazers = RepositoryMetric("stargazers_count")
        self.watchers = RepositoryMetric("watchers_count")
        self.forks = RepositoryMetric("forks_count")
        self.views = RepositoryTrafficMetric("views", "count")
        self.unique_vistors = RepositoryTrafficMetric("views", "uniques")
        self.clones = RepositoryTrafficMetric("clones", "count")
        self.unique_cloners = RepositoryTrafficMetric("clones", "uniques")
     
    def print_metrics(self) -> None:
        """
        Prints all tracked metrics.
        
        Returns:
            None.
        """
        
        print("Stargazers: ")
        self.stargazers.print_metrics()
        print("######################\n")

        
        print("Watchers: ")
        self.watchers.print_metrics()
        print("######################\n")


        print("Forks: ")
        self.forks.print_metrics()
        print("######################\n")
        

        print("Views: ")
        self.views.print_metrics()
        print("######################\n")
        

        print("Unique Visitors: ")
        self.unique_vistors.print_metrics()
        print("######################\n")
        
        
        print("Cloners: ")
        self.clones.print_metrics()
        print("######################\n")\
           
            
        print("Unique Cloners: ")
        self.unique_cloners.print_metrics()
        print("######################\n")
