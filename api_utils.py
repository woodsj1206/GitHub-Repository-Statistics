import asyncio
import httpx
import time
import calendar

class GitHubAPIHandler:
    """
    Handles GitHub API requests with built-in support for authentication, retries, and rate limit handling.
    """
    

    def __init__(self, personal_access_token: str, retries=3, delay=2):
        """
        Initializes the GitHubAPIHandler instance with authentication and retry settings.

        Args:
            personal_access_token (str): GitHub personal access token for authentication.
            retries (int, optional): Number of times to retry a failed request. Defaults to 3.
            delay (int, optional): Delay (in seconds) between retries. Defaults to 2.
        """
        
        self.retries = retries
        self.delay = delay
        self.request_headers = {"Authorization": f"Bearer {personal_access_token}"}


    async def get_response(self, url: str, backoff_factor=2):
        """
        Sends an asynchronous GET request to the specified URL and returns the response object.

        Args:
            url (str): The URL to which the GET request will be sent.
            backoff_factor (int, optional): Factor used to calculate the retry delay. 
                                            It helps to increase the delay between retries exponentially. Defaults to 2. 

        Returns:
            httpx.Response: The raw response object if the request is successful (status code 200). 
            None: After retrying the specified number of attempts if unsuccessful.
        """

        # Calculate the total number of attempts (initial request + retries)
        total_attempts = 1 + self.retries
    
        async with httpx.AsyncClient() as client:
            
            # Attempt the request up to 'retries' times
            for i in range(total_attempts):
                try:
                    # Send the GET request with the provided URL and authorization headers
                    response = await client.get(url, headers=self.request_headers)
                
                    # Log the URL requested and the status code received
                    print(f"Attempt {i + 1}: GET {url} -> STATUS CODE: {response.status_code}")
                
                    # Handle GitHub API rate limits based on response headers
                    await self.handle_rate_limit(response.headers)
            
                    # Check if the request was successful (status code 200)
                    if response.status_code == 200:
                        return response             # Return the response if successful

                except Exception as e:
                    # Print the exception message if an error occurs during the request
                    print(f"An exception occurred: {e}")
        
                # Wait before next retry (if not the last attempt)
                if i < self.retries:
                    retry_delay = self.delay * (backoff_factor ** (i + 1))
                    print(f"Retrying {url} after {retry_delay} seconds...\n")
                    await asyncio.sleep(retry_delay)
            
        # Return None if all retry attempts fail
        return None


    async def handle_rate_limit(self, response_headers: dict[str, str]) -> None:
        """
        Checks GitHub API rate limits and waits if the limit is exceeded.

        Args:
            response_headers (dict): Response headers containing rate limit info.

        Returns:
            None.
        """
        
        # Extract the number of remaining requests from the response headers
        remaining_requests = int(response_headers.get("X-RateLimit-Remaining", 0))
        print(f"Request Remaining: {remaining_requests}")
        
        # Check if the rate limit has been exceeded
        if remaining_requests <= 0:
            # Extract the time (in Unix epoch) when the rate limit will reset
            rate_limit_reset_epoch = int(response_headers.get("X-RateLimit-Reset", 0))
        
            # Get the current time in Unix epoch
            current_time_epoch = calendar.timegm(time.gmtime())

            # Calculate how many seconds to wait until the rate limit resets (+1 second buffer)
            seconds_until_reset = rate_limit_reset_epoch - current_time_epoch + 1

            # Convert reset time from epoch to a readable format (GMT)
            reset_time_struct = time.localtime(rate_limit_reset_epoch)
            formatted_reset_time = time.strftime("%m/%d/%Y %H:%M:%S GMT", reset_time_struct)

            # Inform the user about the wait time
            print(f"Rate limit exceeded: Resuming at {formatted_reset_time} after waiting {seconds_until_reset} seconds...")

            # Pause execution until the rate limit resets
            await asyncio.sleep(seconds_until_reset)

        return None