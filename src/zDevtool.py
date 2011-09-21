'''This code will verify the unit tests, update git, and then build the
   plugin .zip package.  It is run when we've made some progress.
   
   It should be noted that this is just for my convenience; I've done
   absolutely no checking to make sure your build environment matches
   mine.  Use at your own risk (or better still, not at all)'''
   
import zUnitTest
import commands
import os

class DevToolProblem(Exception):
    def __init__(self,msg):
        self.msg = msg

def compile_and_setup():
    print '===== Compiling code, creating plugin, cleaing up ====='
    print 'Compiling C++ based modules using distutils'
    try:
        os.chdir('c++')
        status, output = commands.getstatusoutput('python setup.py build_ext --inplace')
        if status:
            raise DevToolProblem('error: {0}'.format(output))
        else:
            print output
        print 'Tidying up'
        status, output = commands.getstatusoutput('mv _OptimizeCompare.so ../_OptimizeCompare.so')
        if status:
            raise DevToolProblem('error: {0}'.format(output))
        status, output = commands.getstatusoutput('mv OptimizeCompare.py ../OptimizeCompare.py')
        if status:
            raise DevToolProblem('error: {0}'.format(output))   
    finally:     
        os.chdir('../')

def run_tests(short = True, medium=True, long=True):
    suites = zUnitTest.build_test_suites()
    skipif = False
    if short:
        print "Running short tests"
        skipif = not zUnitTest.run_suite(suites['short'], 'short', skipif)
    if medium:
        print "Running medium tests"
        skipif = not zUnitTest.run_suite(suites['medium'],'medium', skipif)
    if long:
        print "Running long tests"
        skipif = not zUnitTest.run_suite(suites['long'],'long', skipif)
    if not skipif:
        return True
    else:
        return False

def update_git():
    try:
        os.chdir('../')
        status, output = commands.getstatusoutput('git add -A')
        if status:
            raise DevToolProblem('error: {0}'.format(output))
        else:
            print output
        status, output = commands.getstatusoutput('git diff --cached')
        if status:
            raise DevToolProblem('error: {0}'.format(output))
        print output
        print '===Changed and Added files:=============================='
        lines = output.split('\n')
        for line in lines:
            if line.find('+++ b') > -1:
                print line
        print '========================================================='
        choice = raw_input('Accept these changes? (y/n)')
        if 'n' == choice.lower():
            status, output = commands.getstatusoutput('git reset .')
            if status:
                raise DevToolProblem('error: {0}'.format(output))
            else:
                print output
        if 'y' == choice.lower():
            msg = raw_input('Enter commit message')
            status, output = commands.getstatusoutput('git commit -m "{0}"'.format(msg))
            print output
            if status and not output.find('nothing to commit'):
                raise DevToolProblem('error: {0}'.format(output))
            choice = raw_input('Update remote repository? (y/n)')
            if 'y' == choice.lower():
                status, output = commands.getstatusoutput('git push -u origin master')
                print output
                if status and not output.find('nothing to commit'):
                    raise DevToolProblem('error: {0}'.format(output))
    finally:
        os.chdir('src')
    
if __name__ == '__main__':
    try:
        input = ''
        compile_and_setup()
        while not 'q' == input.lower():
            print "Choose:"
            print "1) Run quick tests"
            print "2) Run quick and medium tests"
            print "3) Run quick, medium, and long tests"
            print "G) Run quick and medium tests, then update git"
            print "Q) Quit"
            input = raw_input()

            if '1' == input:
                run_tests(True,False,False)
            elif '2' == input:
                run_tests(True,True,True)
            elif '3' == input:
                run_tests(True,True,True)
            elif 'g' == input.lower():
                result = run_tests(True,True,False)
                if result:
                    update_git()         
        print 'Devtool completed.'
    except DevToolProblem as e:
        print "Encountered a problem.  The error was:"
        print e.msg

                        