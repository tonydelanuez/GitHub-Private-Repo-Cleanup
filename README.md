# GitHub Private Repo Cleanup

This utility helps back up your private GitHub repositories locally before deleting them off of your GitHub account - useful for migrating off of student accounts to avoid being billed. You can also use this script to make your private repos public (omitting whichever repositories you want). 

In order to use this script, you must first create a [GitHub Access Token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/) and [assign it to the environment variable](https://askubuntu.com/questions/58814/how-do-i-add-environment-variables)  $GITHUB_ACCESS_TOKEN in your terminal. 

Usage:

    python cleanup.py <github username>

Optional flags:

    --no-delete: this flag will specify not to delete any repos. Use this if you would only like to clone all your repos.
    
    --no-clone: use this flag with caution! If you use it, your repositories will NOT be cloned before deletion.
    
    --skip <repo1> <repo2> <repo3> ... : use this to skip over certain repositories for cloning/deletion. 
    
    --make-public  use this flag to just make your private repos public. PLEASE BE SURE THIS DATA CAN GO PUBLIC.

You'll need to install gitpython for this to work: 

    pip install gitpython
    
DISCLAIMER: I AM NOT RESPONSIBLE FOR ANY DATA YOU HAPPEN TO ERRONEOUSLY DELETE OR MAKE PUBLIC. USE THIS TOOL CAREFULLY. 
