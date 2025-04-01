Use @web:https://help.alteryx.com/20232/en/server/api-overview.html to create an Alteryx Server API package written in Python database. follow the details in the @docs:planning.md and @docs:tasks.md for initial guidance on the implementation. The wrapper is to interact with an alteryx server instance needs to interact with the api to do the following:

- authenticate to the alteryx server
- List workflows
- Create a new workflow
- Update an existing workflow
- Delete an existing workflow
- add a workflow to the job queue

Be sure to give comprehensive descriptions for each api interaction method as well as the parameters and return values users will need to know.

Follow the best practices and modern http interaction patterns for creating api wrappers.

After creating the initial package, update README.md and TASK.md since you now have the initial implementation for the package. If part of the high level vision or architecture has changed, update the planning document.