import os
import sys
import argparse
import requests
from requests.auth import HTTPBasicAuth
from git import Repo

parser = argparse.ArgumentParser(description='GitHub private repository cloning and deletion. Remember to set your GITHUB_ACCESS_TOKEN variable')
parser.add_argument('user', help="username for GitHub account")
parser.add_argument('--skip', nargs='+')
parser.add_argument('--no-delete', help="use this flag to specify no deletion of repos", action="store_true")
parser.add_argument('--no-clone', help="use this flag to specify no cloning of repos", action="store_true")
GITHUB_API_BASE_URL = 'https://api.github.com'
args = parser.parse_args()
GITHUB_ACCESS_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN')
if GITHUB_ACCESS_TOKEN is None:
    print("GITHUB_ACCESS_TOKEN environment variable not set")
    sys.exit(1)

GITHUB_USER = args.user
# flags for clone/delete
clone_flag = not args.no_clone
delete_flag = not args.no_delete
skipped_repos = args.skip or []

def main():
    # Reading and parsing arguments
    session = create_github_session()
    set_git_environment()
    repos = get_private_repo_names(session, skipped_repos)
    if not repos:
        print("No repos to delete or clone.")
    else:
        clone_and_or_delete(repos, session)
        print("Done.")

# from user vincenta on this gist: https://gist.github.com/garrettdreyfus/8153571
def confirm(question):
    while "the answer is invalid":
        reply = str(raw_input(question+' (y/n): ')).lower().strip()
        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False

# environment variables must be set in order to clone a repository
def set_git_environment():
    os.environ['GIT_USERNAME'] = GITHUB_USER
    os.environ['GIT_PASSWORD'] = GITHUB_ACCESS_TOKEN
    print("Git environment variables set for GitHub account")

# make a requests.Session() in order to perform multiple REST actions with same Auth
def create_github_session():
    session = requests.Session()
    session.auth = (GITHUB_USER, GITHUB_ACCESS_TOKEN)
    login_response = session.get('https://api.github.com/user')
    if login_response.ok:
        print("Connected to GitHub successfully as user %s." % GITHUB_USER)
    else:
        print("Could not connect to GitHub!")
        sys.exit(1)
    return session

# Use GitHub API to get private repositories where you are owner
def get_private_repo_names(session, skipped):
    if skipped:
        print("Skipping repositories: %s" % " ".join(skipped))
    repos_url = "%s/user/repos?type=private" % GITHUB_API_BASE_URL
    response = session.get(repos_url)
    if not response.ok:
        print("Could not get private repos.")
        sys.exit(1)
    private_repos = [str(repo["name"]) for repo in response.json() if repo['owner']['login'] == GITHUB_USER and str(repo["name"]) not in skipped]
    print("Your selected private repositories are:")
    for idx, repo in enumerate(private_repos):
        print("\t %d.%s" % (idx+1, repo))
    return private_repos

# make a /cloned folder if one doesn't exist, then clone the repository.
def clone_repository(repo_owner, repo_name):
    # Create a place to store all the cloned repos
    if not os.path.isdir('cloned'):
        print("Creating directory ./cloned")
        os.makedirs('cloned')
    print("Cloning repository %s..." % repo_name)
    repo_url = "https://github.com/%s/%s" % (repo_owner, repo_name)
    # Attaching the access token to the clone URL
    auth_string = "://%s:x-oauth-basic@" % GITHUB_ACCESS_TOKEN
    auth_repo_url = repo_url.replace('://', auth_string)
    clone_dir = 'cloned/'+repo_name
    repo = None
    if os.path.isdir(clone_dir):
        print("Already have a repo here with the name %s!" % repo_name)
    else:
        os.makedirs(clone_dir)
        repo = Repo.clone_from(auth_repo_url, clone_dir)
    # validate that clone worked
    clone_status = repo is not None
    if clone_status:
        print("Cloned repository %s." % repo_name)
    else:
        print("Could not clone repository: %s " % repo_name)
    return clone_status

# delete the repository using the GitHub REST API
def delete_repository(repo_owner, repo_name, session):
    print("Attempting to delete repo: %s..." % repo_name)
    delete_url = "%s/repos/%s/%s" % (GITHUB_API_BASE_URL, repo_owner, repo_name)
    delete_response = session.delete(delete_url)
    if delete_response.ok:
        print("Repository %s successfully deleted." % repo_name)
    else:
        print("Could not delete repository %s!" % repo_name)
    return delete_response.ok

# perform all repo clones or deletion, needs the GitHub session for auth.
def clone_and_or_delete(repos, session):
    print("Actions:")
    print("\t Clone: %s" % (clone_flag))
    print("\t Delete: %s" % (delete_flag))
    want_delete = confirm("Are you sure you want to continue?")
    repos_deleted = []
    repos_cloned = []
    if not want_delete:
        print("Okay, exiting.")
        sys.exit(1)
    else:
        print("Deleting your private repos.")
    for repo in repos:
        clone_success = False
        if clone_flag:
            clone_success = clone_repository(GITHUB_USER, repo)
            if clone_success:
                repos_cloned.append(repo)
        if delete_flag:
            delete_confirm = True
            if clone_flag and not clone_success:
                delete_confirm = confirm("Clone failed. Still okay to delete repo %s?" % repo)
            if delete_confirm:
                delete_success = delete_repository(GITHUB_USER, repo, session)
                if delete_success:
                    repos_deleted.append(repo)
    print("%d repos cloned: " % (len(repos_cloned)), repos_cloned)
    print("%d repos deleted: " % (len(repos_deleted)), repos_deleted)

if __name__=='__main__':
    main()
