'''This code will verify the unit tests, update git, and then build the
   plugin .zip package.  It is run when we've made some progress.
   
   It should be noted that this is just for my convenience; I've done
   absolutely no checking to make sure your build environment matches
   mine.  Use at your own risk (or better still, not at all)'''
   
import UnitTests
import commands
import os

if __name__ == '__main__':
    print 'Verifying program correctness with Unit Tests'
    if not UnitTests.runTests():
        print 'Unit Tests failed; stopping here'
    else:
        os.chdir('../')
        status, output = commands.getstatusoutput('git add -A')
        if status:
            print 'error: {0}'.format(output)
            print 'Error staging files for Git; stopping here'
        else:
            status, output = commands.getstatusoutput('git diff --cached')
            if status:
                print 'error: {0}'.format(output)
                print 'Error staging files for Git; stopping here'
            else:
                print output
                choice = raw_input('Accept these changes? (y/n)')
                if 'y' == choice.lower():
                    msg = raw_input('Enter commit message')
                    status, output = commands.getstatusoutput('git commit -m "{0}"'.format(msg))
                    print output
                    if status and not output.find('nothing to commit'):
                        print 'Error commiting to Git; stopping here'
                    else:
                        choice = raw_input('Update remote repository? (y/n)')
                        if 'y' == choice.lower():
                            status, output = commands.getstatusoutput('git push -u origin master')
                            print output
                            if status and not output.find('nothing to commit'):
                                    print 'Error commiting to Github'
                        print 'Devtool completed.'