from git import Repo
import os
import sys  

#reload(sys)  
#sys.setdefaultencoding('utf8')

os.chdir('/home/ec2-user/hectoramirez.github.io/covid')

PATH_OF_GIT_REPO = r'/home/ec2-user/hectoramirez.github.io/.git'  # make sure .git folder is properly configured
COMMIT_MESSAGE = 'daily update'


def git_push():

    repo = Repo(PATH_OF_GIT_REPO)
    repo.git.add('--all')  # update=True)
    repo.index.commit(COMMIT_MESSAGE)
    origin = repo.remote(name='origin')
    origin.push()


git_push()
