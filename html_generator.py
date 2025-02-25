from repository_metric import RepositoryMetric, RepositoryMetricsTracker

class GitHubRepoMetricsHTMLGenerator:
    """
    A class to generate HTML content displaying GitHub repository metrics, 
    including user information, repository links, and customizable themes.
    """


    def __init__(self, user_name: str, theme="light", profile_link_displayed=True, repository_links_displayed=True):
        """
        Initializes the HTML generator for GitHub repository metrics.

        Args:
            theme (str): The theme for the HTML output. Default is "light".
            user_name (str): GitHub username of the user.
            html_content (str): HTML output.
            profile_link_displayed (bool): Determines if the GitHub profile link should be displayed. Default is True.
            repository_links_displayed (bool): Determines if links to repositories should be displayed. Default is True.
        """
        self.html_content = ""
        self.user_name = user_name
        self.theme = theme
        self.profile_link_displayed = profile_link_displayed
        self.repository_links_displayed = repository_links_displayed


    def create_html_file(self, filename: str):
        """
        Creates an HTML file with the given filename and content.

        Args:
            filename (str): The name of the HTML file to create (e.g., "index.html").
        """
        
        try:
            with open(filename, "w") as file:
                file.write(self.html_content)
                
            print(f"HTML file '{filename}' created successfully.")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            

    def format_large_number(self, number):
        """
        Formats large numbers into a readable string with appropriate suffixes (k, M, B).

        Args:
            number (int or float): The number to be formatted.

        Returns:
            str: The formatted string representing the number with a suffix:
                 - 'k' for thousands
                 - 'M' for millions
                 - 'B' for billions
                 - '1B+' if the number exceeds one billion

        The function performs the following:
        - Checks if the number exceeds one billion and returns '1B+' for simplicity.
        - Iterates through predefined factors and suffixes, formatting the number accordingly.
        - Ensures no unnecessary trailing zeros or decimal points are included.
        - Returns the original number as a string if it doesn't meet any factor criteria.
        """
        # Simplify extremely large numbers by returning '1B+' if greater than one billion
        if number > 1_000_000_000:
            return "1B+"

        # Iterate through factor-suffix pairs for billions, millions, and thousands
        for factor, suffix in [(1_000_000_000, 'B'), (1_000_000, 'M'), (1_000, 'k')]:
            if number >= factor:
                # Format number with one decimal place, remove trailing zeros and dots
                formatted = f"{number / factor:.1f}".rstrip('0').rstrip('.')
                return f"{formatted}{suffix}"

        # Return the number as a string if it doesn't meet any scaling factor
        return str(number)


    def generate_anchor_tag(self, link_text: str, url: str) -> str:
        """
        Creates an HTML anchor tag (`<a>`) with the given text and URL.

        Args:
            link_text (str): The text to display for the link.
            url (str): The URL to which the anchor tag should point.

        Returns:
            str: A string containing the HTML anchor tag in the format:
            <a class="link" href="url">link_text</a>
        """

        return f'<a class="link" target="_blank" href="{url}">{link_text}</a>'
    
    
    def generate_css_variables(self, css_variables: dict[str, str]) -> str:
        """
        Generates CSS custom properties based on the given theme dictionary.

        Args:
            css_variables (dict): A dictionary containing CSS property names and their corresponding values.
                            Example: {"background-color": "#ffffff", "text-color": "#000000"}

        Returns:
            str: A string containing CSS custom properties in the format:
                    --property-name: value;
        """
        
        css_variables_str = ""
        
        for property_name in css_variables:
             css_variables_str += f"--{property_name}: {css_variables[property_name]};\n"
             
        return css_variables_str


    def generate_html_for_metrics(self, metric_tracker: RepositoryMetricsTracker) -> str:
        """
        Generates HTML content for displaying repository metrics, applying the selected theme.

        Args:
            metric_tracker (RepositoryMetricsTracker): An object that tracks repository metrics (not used in the snippet but assumed to be part of the class).

        Returns:
            str: The generated HTML content with the selected theme applied.
        """
        
        light_theme_styles  = {"background-color": "#ffffff",
                               "border-color": "#59636e", 
                               "icon-color": "#59636e", 
                               "link-color" : "#59636e",
                               "link-hover-color" : "#023b95",
                               "logo-icon-color" : "#59636e",
                               "text-color": "#59636e", }

        dark_theme_styles  = {"background-color": "#010409",
                              "border-color": "#dfe1ed", 
                              "icon-color": "#dfe1ed", 
                              "link-color" : "#dfe1ed",
                              "link-hover-color" : "#74b9ff",
                              "logo-icon-color" : "#dfe1ed",
                              "text-color": "#dfe1ed", }
        
        svg_icons = {"dot": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><path d="M4 8a4 4 0 1 1 8 0 4 4 0 0 1-8 0Zm4-2.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z"></path></svg>',
                     "eye": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><path d="M8 2c1.981 0 3.671.992 4.933 2.078 1.27 1.091 2.187 2.345 2.637 3.023a1.62 1.62 0 0 1 0 1.798c-.45.678-1.367 1.932-2.637 3.023C11.67 13.008 9.981 14 8 14c-1.981 0-3.671-.992-4.933-2.078C1.797 10.83.88 9.576.43 8.898a1.62 1.62 0 0 1 0-1.798c.45-.677 1.367-1.931 2.637-3.022C4.33 2.992 6.019 2 8 2ZM1.679 7.932a.12.12 0 0 0 0 .136c.411.622 1.241 1.75 2.366 2.717C5.176 11.758 6.527 12.5 8 12.5c1.473 0 2.825-.742 3.955-1.715 1.124-.967 1.954-2.096 2.366-2.717a.12.12 0 0 0 0-.136c-.412-.621-1.242-1.75-2.366-2.717C10.824 4.242 9.473 3.5 8 3.5c-1.473 0-2.825.742-3.955 1.715-1.124.967-1.954 2.096-2.366 2.717ZM8 10a2 2 0 1 1-.001-3.999A2 2 0 0 1 8 10Z"></path></svg>',
                     "mark-github": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path></svg>',
                     "repo-forked": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><path d="M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"></path></svg>',
                     "star": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Zm0 2.445L6.615 5.5a.75.75 0 0 1-.564.41l-3.097.45 2.24 2.184a.75.75 0 0 1 .216.664l-.528 3.084 2.769-1.456a.75.75 0 0 1 .698 0l2.77 1.456-.53-3.084a.75.75 0 0 1 .216-.664l2.24-2.183-3.096-.45a.75.75 0 0 1-.564-.41L8 2.694Z"></path></svg>',
                     }
        
        themes = {
            "light": light_theme_styles, 
            "dark": dark_theme_styles
        }
        
        selected_theme = themes[self.theme]
        
        self.html_content = f"""
            <!DOCTYPE html>
            <html>
              <head>
                <style>
                  :root {{
                      {self.generate_css_variables(selected_theme)}
                  }}

                  .icon{{
                      display: flex;
                      align-items: center;
                  }}
                  
                  .header-icon{{
                      justify-content: flex-end;
                      color: var(--logo-icon-color);
                  }}

                  .icon-label-container{{
                      display: flex;
                      gap: 5px;
                      width: 200px;
                      white-space: nowrap;
                      text-overflow: ellipsis;
                      overflow: hidden;
                  }}

                  .title{{
                      gap: unset;
                      margin-top: 5px;
                      margin-bottom: 10px;
                      width: 100%;
                  }}

                  .link{{
                      color: var(--link-color);
                      transition: color 0.3s ease-in-out;
                      text-decoration: none;
                  }}
      
                  .link:hover{{
                      color: var(--link-hover-color);
                  }}

                  .data{{
                      width: 100px;
                      display: flex;
                      justify-content: flex-end;
                  }}

                  .repo-metric{{
                      display: flex;
                      justify-content: space-between;
                  }}

                  .container{{
                      display: flex;
                      flex-direction: column;
                  }}

                  .label{{
                      overflow: hidden;
                      text-overflow: ellipsis;
                      white-space: nowrap;
                      flex: 1;
                  }}

                  .label p, .data p{{
                      margin-block-start: 0.25em;
                      margin-block-end: 0.25em;
                      overflow: hidden;
                      text-overflow: ellipsis;
                      white-space: nowrap;
                  }}

                  .card{{
                      font-family: "Segoe UI";
                      padding: 20px 30px 20px 30px;
                      width: 350px;
                      height: 350px;
                      overflow: auto;
                      border: 1px;
                      border-style: solid;
                      border-color: var(--border-color);
                      background-color: var(--background-color)
                  }}

                  .text {{
                      color: var(--text-color);
                      font-weight: 500;
                  }}

                  .icon svg {{
                      fill: var(--icon-color)
                  }}

                  .header{{
                      font-size: 0.75rem;
                  }}

                  .sub-header-1{{
                      font-size: 0.70rem;
                      padding-left: 20px;
                  }}

                  .sub-header-2{{
                      font-size: 0.70rem;
                      padding-left: 40px;
                  }}
                  .sub-header-1 .icon svg, .sub-header-2 .icon svg{{
                      height: 12px;
                      width: 12px;
                  }}
                </style>
              </head>
              <body>
                <div class="card">
                  <div class="container">
                    <div class="repo-metric-container">
                      <div class="repo-metric header">
                        <div class="icon-label-container title">
                          <div class="icon"></div>
                          <div class="label">
                            <p class="text">GitHub Repository Statistics for {self.generate_anchor_tag(self.user_name.title(), f"https://github.com/{self.user_name}") if self.profile_link_displayed else self.user_name.title()}</p>
                          </div>
                        </div>
                        <div class="data">
                          <div class="icon title header-icon">{svg_icons["mark-github"]}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                <div class="container">
                  <div class="repo-metric-container">
                    <div class="repo-metric header">
                        <div class="icon-label-container">
                            <div class="icon">
                                {svg_icons["star"]}
                            </div>
                            <div class="label">
                                <p class="text">Stars</p>
                            </div>
                        </div>
                        <div class="data">
                            <p class="text"></p>
                        </div>
                    </div>
                   </div>
                    {self.generate_repo_metric_container("Stargazers", "Starred", metric_tracker.stargazers, svg_icons["dot"])}
                  </div>
                  <div class="container">
                    <div class="repo-metric-container">
                      <div class="repo-metric header">
                        <div class="icon-label-container">
                            <div class="icon">
                              {svg_icons["eye"]}
                            </div>
                            <div class="label">
                              <p class="text">Views (past 14 days)</p>
                            </div>
                        </div>
                        <div class="data">
                          <p class="text"></p>
                        </div>
                      </div>
                    </div>  
                      {self.generate_repo_metric_container("Watchers", "Watched", metric_tracker.watchers, svg_icons["dot"])}
                      {self.generate_repo_metric_container("Views", "Viewed", metric_tracker.views, svg_icons["dot"])}
                      {self.generate_repo_metric_container("Unique Visitors", "Unique Visitors", metric_tracker.unique_vistors, svg_icons["dot"])}
                   </div>
                  <div class="container">
                    <div class="repo-metric-container">
                      <div class="repo-metric header">
                        <div class="icon-label-container">
                          <div class="icon">
                            {svg_icons["repo-forked"]}
                          </div>
                          <div class="label">
                            <p class="text">Distribution</p>
                          </div>
                        </div>
                        <div class="data">
                          <p class="text"></p>
                        </div>
                      </div>
                    </div>
                    {self.generate_repo_metric_container("Clones", "Cloned", metric_tracker.clones, svg_icons["dot"])}
                    {self.generate_repo_metric_container("Unique Cloners", "Unique Cloners", metric_tracker.unique_cloners, svg_icons["dot"])}
                    {self.generate_repo_metric_container("Forks", "Forked", metric_tracker.forks, svg_icons["dot"])}
                  </div>
                </div>
              </body>
            </html>
            """
        
        return self.html_content


    def generate_repo_metric_container(self, metric_display_name: str, metric_past_tense_name: str, repository_metric: RepositoryMetric, bullet_point_icon_svg: str) -> str:
        """
        Args:
            metric_display_name (str): The plural form of the metric name (e.g., "Stargazers").
            metric_past_tense_name (str): The past tense of the metric name (e.g., "Starred").
            repository_metric (RepositoryMetric): Object containing traffic metric data for repositories.
            bullet_point_icon_svg (str): SVG markup for bullet points next to sub-sections.

        Returns:
            str: A formatted HTML string representing the repository traffic metric section.
        """
        
        html_content = ""
    
        html_content += f"""
                <div class="repo-metric-container">
                    <div class="repo-metric sub-header-1">
                        <div class="icon-label-container">
                            <div class="icon">
                                {bullet_point_icon_svg}
                            </div>
                            <div class="label">
                                <p class="text">Total {metric_display_name}</p>
                            </div>
                        </div>
                        <div class="data">
                            <p class="text">{self.format_large_number(repository_metric.total_metric_count)}</p>
                        </div>
                    </div>
                </div>
                <div class="repo-metric-container">
                    <div class="repo-metric sub-header-1">
                        <div class="icon-label-container">
                            <div class="icon">
                                {bullet_point_icon_svg}
                            </div>
                            <div class="label">
                                <p class="text">Most {f"{metric_display_name}" if metric_display_name == metric_past_tense_name else f"{metric_past_tense_name} Repositor{self.get_plural_suffix(repository_metric.get_top_repositories())}"}
                            </div>
                        </div>
                        <div class="data">
                            <p class="text">{self.format_large_number(repository_metric.max_metric_count)}</p>
                        </div>
                    </div>
                    {self.generate_repo_sub_header_html(repository_metric.get_top_repositories(), bullet_point_icon_svg)}
                </div>
        """
            
        return html_content
    
        
    def generate_repo_sub_header_html(self, repositories: list, bullet_point_svg) -> str:
        """
        Generates HTML markup for displaying a list of repository names with associated icons.
    
        Args:
            repo_names (list): A list of repository names (strings).
    
        Returns:
            str: HTML string representing each repository in a sub-header section.
        """
    
        html_content = ""
    
        for repository_name in repositories:
            html_content += f"""
                <div class="repo-metric sub-header-2">
                  <div class="icon-label-container">
                    <div class="icon">
                      {bullet_point_svg}
                    </div>
                    <div class="label">
                      <p class="text">{self.generate_anchor_tag(repository_name, f"https://github.com/{self.user_name}/{repository_name}") if self.repository_links_displayed else repository_name}</p>
                    </div>
                  </div>
                  <div class="data">
                    <p class="text"></p>
                  </div>
                </div>
            """
            
        return html_content


    def get_generated_html(self) -> str:
        """
        Retrieves the generated HTML content.

        Returns:
            str: The HTML content generated by the class.
        """
        
        return self.html_content


    def get_plural_suffix(self, repositories: list) -> str:
        """
        Returns the appropriate plural suffix ('y' or 'ies') based on the number of repositories.

        Args:
            repositories (list): A list of repository names.

        Returns:
            str: 'y' if there is one repository, 'ies' otherwise.
        """
        
        return "y" if len(repositories) < 2 else "ies"