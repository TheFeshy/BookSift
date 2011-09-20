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

if __name__ == '__main__':
    try:
        print 'Compiling C++ based modules using gcc and swig'
        os.chdir('c++')
        status, output = commands.getstatusoutput('swig -python OptimizeCompare.i')
        if status:
            raise DevToolProblem('error: {0}'.format(output))
        flags = "/usr/include/python2.7"
        status, output = commands.getstatusoutput('gcc -O2 -fPIC -c OptimizeCompare.cpp OptimizeCompare_wrap.c -I{0}'.format(flags))
        if status:
            raise DevToolProblem('error: {0}'.format(output))
        status, output = commands.getstatusoutput('gcc -shared OptimizeCompare.o OptimizeCompare_wrap.o -o _OptimizeCompare.so')
        if status:
            raise DevToolProblem('error: {0}'.format(output))
        status, output = commands.getstatusoutput('mv _OptimizeCompare.so ../_OptimizeCompare.so')
        if status:
            raise DevToolProblem('error: {0}'.format(output))
        status, output = commands.getstatusoutput('mv OptimizeCompare.py ../OptimizeCompare.py')
        if status:
            raise DevToolProblem('error: {0}'.format(output))
        os.chdir('../')
        print 'Verifying program correctness with Unit Tests'
        if not zUnitTest.runTests():
            raise DevToolProblem('Unit Tests failed; stopping here')        
        os.chdir('../')
        status, output = commands.getstatusoutput('git add -A')
        if status:
            raise DevToolProblem('error: {0}'.format(output))
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
        print 'Devtool completed.'
    except DevToolProblem as e:
        print "Encountered a problem.  The error was:"
        print e.msg

                        