# My submission for VGGvirtualinternship coding test
Email: Orjikalukelvin@gmail.com
username: Kelvin Orji
Name: Orji kalu kelvin
#python 


## RESOURCES
Python
framework: flask-restful
Database: SQLite3
ORM: SQLalchemy
Cloud Infrastructure: Heroku
Version control: Git and Github


## Heroku Link
https://vggcodingtest.herokuapp.com/

Get https://vggcodingtest.herokuapp.com/projects retrieve all projects

Post https://vggcodingtest.herokuapp.com/projects/  you have to provide a unique name and a description parameter eg https://vggcodingtest.herokuapp.com/projects args name=project5&&description=mydescription

Get https://vggcodingtest.herokuapp.com/<projectid> eg  https://vggcodingtest.herokuapp.com/projects/1 gets a project with id 1

put https://vggcodingtest.herokuapp.com/<projectid> eg  https://vggcodingtest.herokuapp.com/projects/1  args description=changed updates description


Patch https://vggcodingtest.herokuapp.com/<projectid> eg  https://vggcodingtest.herokuapp.com/projects/1?completed=true takes arg "true" or "false" 


Delete  https://vggcodingtest.herokuapp.com/<projectid> eg  https://vggcodingtest.herokuapp.com/projects/1 deletes a project with given id

post https://vggcodingtest.herokuapp.com/projects/1/actions  creates an action belonging to project with id 1. takes argument note and description 


get https://vggcodingtest.herokuapp.com/actions Retrieves all actions

get https://vggcodingtest.herokuapp.com/projects/1/actions retrieves all actions associated with project with id 1

get https://vggcodingtest.herokuapp.com/actions/1 Retrieves a action with action id 1


get https://vggcodingtest.herokuapp.com/projects/1/actions/1 retrieves all actions with action id 1 and project id 1

put https://vggcodingtest.herokuapp.com/projects/1/actions/1 updates the action with id 1 and associated with project id 1 takes note and description as argument

delete https://vggcodingtest.herokuapp.com/projects/1/actions/1 delete action with id 1 and project id 1


## Git Link.
https://github.com/VINKELA/codingtest.git

