## FEATURE:

Build a robust and secure Python wrapper for the Alteryx Server API to enable automated Continuous Integration/Continuous Delivery (CI/CD) pipelines for publishing the resulting Python package to PyPI. This project leverages modern Python tooling: UV for package/environment management, Ruff for linting/formatting, and Pytest for testing.


## DOCUMENTATION:
 
- url: https://spider.theinformationlab.co.uk/webapi//swagger/ui/index  
  why: Example Alteryx Server API Swagger documentation for endpoint details and schemas. 

- url: https://help.alteryx.com/current/en/server.html  
  why: Official Alteryx Server Help pages for API documentation and general server information.

- url: https://requests.readthedocs.io/en/latest/
  why: Documentation for the requests package for quering external api endpoints

- url: https://requests-oauthlib.readthedocs.io/en/latest/
  why: Documentation for oauth query support library for the requests package

- url: https://docs.astral.sh/uv/  
  why: Official UV documentation for package and environment management.

- url: https://docs.astral.sh/ruff/  
  why: Official Ruff documentation for linting and formatting.**

- url: https://github.com/Sivivatu/AlteryxGalleryAPI/tree/workflow-methods  
  why: Existing project codebase to build upon, including current development branch.

- url: https://github.com/coleam00/context-engineering-intro  
  why: Context Engineering repository for planning and development steps.

- url: https://docs.astral.sh/ty  
  why: Documentation for \`ty\` (Red Knot), the experimental type checker from Astral, for evaluation.


## OTHER CONSIDERATIONS:

- Include a .env.example, README with instructions for setup including how to configure configuring API keys.
- Include the project structure in the README.
- Virtual environment has already been set up with the necessary dependencies.
- Use python_dotenv and load_env() for environment variables