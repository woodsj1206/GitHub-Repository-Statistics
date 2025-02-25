import csv
from datetime import datetime
import repository_metric

class CSVReportGenerator:
    """
    Handles CSV generation for repository and traffic metrics reports.
    Provides utilities for writing CSV files and formatting timestamps.
    """
    

    def format_timestamp(self, timestamp: str) -> str:
        """
        Converts ISO 8601 timestamp to MM/DD/YYYY format.

        Args:
            timestamp (str): Timestamp in ISO 8601 format (e.g., '2025-02-10T00:00:00Z').

        Returns:
            str: Formatted date as MM/DD/YYYY.
        """
        
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").strftime("%m/%d/%Y")
        

    def generate_repository_metrics_report(self, metric_tracker: repository_metric.RepositoryMetricsTracker, filename="repository_metrics_report"):
        """
        Generates a CSV report with total repository metrics: Stars, Watchers, and Forks.

        Args:
            metric_tracker (RepositoryMetricsTracker): Tracker containing repository metrics.
            filename (str, optional): Output CSV filename.
        """
        
        headers = ["Stars", "Watchers", "Forks"]
        data = [[
            metric_tracker.stargazers.total_metric_count,
            metric_tracker.watchers.total_metric_count,
            metric_tracker.forks.total_metric_count
        ]]
        
        
        self.write_csv(f"{filename}.csv", data, headers)
        

    def generate_total_traffic_metrics_report(self, metric_tracker: repository_metric.RepositoryMetricsTracker, filename="total_traffic_metric_report"):
        """
        Generates a CSV report summarizing total traffic metrics over time, including views and clones.

        Args:
            metric_tracker (RepositoryMetricsTracker): Tracker containing all traffic-related metrics.
            filename (str, optional): Output CSV filename.
        """
        
        headers = ["Date", "Total Views", "Unique Visitors", "Total Clones", "Unique Cloners"]
        data = []

        # Iterate through all timestamps, ensuring defaults are set
        for timestamp in metric_tracker.views.total_metric_at_timestamps:
            views = metric_tracker.views.total_metric_at_timestamps.get(timestamp, [0, []])[0]
            unique_visitors = metric_tracker.unique_vistors.total_metric_at_timestamps.get(timestamp, [0, []])[0]
            clones = metric_tracker.clones.total_metric_at_timestamps.get(timestamp, [0, []])[0]
            unique_cloners = metric_tracker.unique_cloners.total_metric_at_timestamps.get(timestamp, [0, []])[0]

            data.append([
                self.format_timestamp(timestamp),
                views,
                unique_visitors,
                clones,
                unique_cloners
            ])

        self.write_csv(f"{filename}.csv", data, headers)


    def generate_traffic_metric_timestamp_report(self, traffic_metric: repository_metric.RepositoryTrafficMetric, filename="traffic_metric_timestamp_report"):
        """
        Generates a CSV report of traffic metrics over time, showing timestamp, repository name, and metric count.

        Args:
            traffic_metric (RepositoryTrafficMetric): Tracker for traffic metrics.
            filename (str, optional): Output CSV filename.
        """
        headers = ["Date", "Repository", f"{traffic_metric.metric_type.title()} {traffic_metric.name.title()}"]
        data = [
            [self.format_timestamp(timestamp), repo[0], repo[1]]
            for timestamp, (_, repositories) in traffic_metric.total_metric_at_timestamps.items()
            for repo in repositories
        ]
        
        self.write_csv(f"{filename}_{traffic_metric.metric_type}_{traffic_metric.name}.csv", data, headers)

  
    def write_csv(self, filename: str, data: list, headers: list = []):
        """
        Writes data to a CSV file.

        Args:
            filename (str): Name of the CSV file.
            data (list): Data rows to write.
            headers (list, optional): Column headers for the CSV file.
        """
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            if headers:
                writer.writerow(headers) 
            writer.writerows(data)