import csv
from datetime import datetime, timezone
import os
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
        

    def generate_repository_metrics_report(self, metric_tracker: repository_metric.RepositoryMetricsTracker, output_folder="", filename="repository_metrics_report") -> None:
        """
        Generates a CSV report with total repository metrics: Stars, Watchers, and Forks.

        Args:
            metric_tracker (repository_metric.RepositoryMetricsTracker): Tracker containing repository metrics.
            output_folder (str, optional): The folder where the CSV file will be saved. If not specified, it will save in the current directory.
            filename (str, optional): Output CSV filename. Defaults to "repository_metrics_report".
        
        Returns:
            None.
        """
        
        current_date = f"{datetime.now(timezone.utc).date()}T00:00:00Z"
        
        headers = ["Date", "Stars", "Watchers", "Forks"]
        data = [[
            self.format_timestamp(current_date),
            metric_tracker.stargazers.total_metric_count,
            metric_tracker.watchers.total_metric_count,
            metric_tracker.forks.total_metric_count
        ]]
        
        
        self.write_csv(f"{filename}.csv", data, output_folder, headers)
        

    def generate_total_traffic_metrics_report(self, metric_tracker: repository_metric.RepositoryMetricsTracker, output_folder="", filename="total_traffic_metric_report") -> None:
        """
        Generates a CSV report summarizing total traffic metrics over time, including views and clones.

        Args:
            metric_tracker (repository_metric.RepositoryMetricsTracker): Tracker containing all traffic-related metrics.
            output_folder (str, optional): The folder where the CSV file will be saved. If not specified, it will save in the current directory.
            filename (str, optional): Output CSV filename. Defaults to "total_traffic_metric_report".
            
        Returns:
            None.
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

        self.write_csv(f"{filename}.csv", data, output_folder, headers)


    def generate_traffic_metric_timestamp_report(self, traffic_metric: repository_metric.RepositoryTrafficMetric, output_folder="", filename="traffic_metric_timestamp_report") -> None:
        """
        Generates a CSV report of traffic metrics over time, showing timestamp, repository name, and metric count.

        Args:
            traffic_metric (repository_metric.RepositoryTrafficMetric): Tracker for traffic metrics.
            output_folder (str, optional): The folder where the CSV file will be saved. If not specified, it will save in the current directory.
            filename (str, optional): Output CSV filename. Defaults to "traffic_metric_timestamp_report".
            
        Returns:
            None.
        """
        
        headers = ["Date", "Repository", f"{traffic_metric.metric_type.title()} {traffic_metric.name.title()}"]
        data = [
            [self.format_timestamp(timestamp), repo[0], repo[1]]
            for timestamp, (_, repositories) in traffic_metric.total_metric_at_timestamps.items()
            for repo in repositories
        ]
        
        self.write_csv(f"{filename}_{traffic_metric.metric_type}_{traffic_metric.name}.csv", data, output_folder, headers)

  
    def write_csv(self, filename: str, data: list, output_folder="", headers: list = []) -> None:
        """
        Writes data to a CSV file.

        Args:
            filename (str): Name of the CSV file.
            data (list): Data rows to write.
            output_folder (str, optional): The folder where the CSV file will be saved. If not specified, it will save in the current directory.
            headers (list, optional): Column headers for the CSV file. Defaults to no headers.
            
        Returns:
            None.
        """
        
        full_filename = os.path.join(output_folder, filename)
        
        with open(full_filename, 'w', newline='') as file:
            writer = csv.writer(file)
            if headers:
                writer.writerow(headers) 
            writer.writerows(data)