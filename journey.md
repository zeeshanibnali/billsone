Alright let us get started!

Let me utilize "uv" package manager in this project as I have noticed it has felt faster and more organized then venv and pip.

Seeing uv's docs, I see ruff, a linter and formatter for python written in rust. This is beneficial, I should have seen this coming. Now I am gonna set up some pre commit hooks, in order for me not to push anything that is not formatted.

Now that ruff has been set up to run everytime I do a git commit, I will start with set up uvicorn and fastapi. uvicorn will handle all the requests and communicate them to fastapi.

Lemme re-read the use case and understand the requirements, apis and responses required.

After having built a few apis for testing, I need swagger for ease in testing and having good docs.
And it is always the best to get started with documentation early on.

Lemme validate the conventions in the project. I need to move away from this single main.py file and organize it into different modules. Every module shall have a controller that will have all the request handling logic and service file for all the db related operations. 
Now I need to add all the relations. Relation between Bills and SubBills.
Seeder shall be beneficial for quick testing here. Will add data for seeding.

Logging Service setup is required for future monitoring.

Lemme add env validations and checks, as missing vars some times bring in frustrating debugging time.

Lemme add handling for escape LIKE literals % and __

Lemme check the schema and handle all the scalability aspects.
