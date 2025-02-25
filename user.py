class User:
     """
     Represents a GitHub user with authentication details and functionality to retrieve repositories.
     """
     

     def __init__(self, user_name: str, personal_access_token: str):
         """
         Initializes a User instance with GitHub username and personal access token.
         
         Args:
            user_name (str): GitHub username of the user.
            personal_access_token (str): Personal access token for authenticating GitHub API requests.
         """
         
         self.user_name = user_name
         self.personal_access_token = personal_access_token