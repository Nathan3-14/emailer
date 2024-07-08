# Emailer
## Use
- Clone the repo and cd into it
- Install any requirements by running `pip install -r "requirements.txt"`
- Create a file titled "s--usr.pass"
- Fill it out like so
```a
user.name@gmail.com
appx pass word
```
- (the app password should be a series of letters)
- Run "main.py"  with the path to the email you want to send (relative to cwd)`python main.py <path>`
- If any errors are encountered, see below
## Common Errors
### Authorisation Error
This may occur if the app password or email is incorrect, please check these values