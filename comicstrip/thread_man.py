''' 
  Author: <adrellias@gmail.com>

  This module handles the creation of threads
  For once off and scheduled continues looping jobs

  Originaly Based on: http://code.activestate.com/recipes/114644/
'''

import time
import threading

class Task( threading.Thread ):
    def __init__( self, action, loopdelay, initdelay , *args ):
        ''' Initiate thread startup '''
        self._action = action
        self._loopdelay = loopdelay
        self._initdelay = initdelay
        self._running = 1

        threading.Thread.__init__( self )


    def __repr__(self):
        ''' Return the options we passed '''
        return '%s %s %s' % (
            self._action, self._loopdelay, self._initdelay )

    def run( self ):
        ''' Run the function we want
        if there is a startup delay set we wait '''
        if self._initdelay:
            time.sleep( self._initdelay )

        self._runtime = time.time()
        while self._running:
            ''' While we are not being told to stop we will run '''
            start = time.time()
            self._action()
            if not self._loopdelay:
                self._running = 0
            else:
                self._runtime += self._loopdelay
                time.sleep( self._runtime - start )

    def stop( self ):
        print 'Sending stop signal'
        self._running = 0

class Scheduler:
      ''' Schedule the threads we want to run'''

      def __init__(self):
          ''' We want a list of tasks ? '''
          self._tasks = []

      def __repr__( self ):
          rep = ''
          for task in self._tasks:
              rep += '%s\n' % `task`
          return rep

      def AddTask( self, action, loopdelay = 0, initdelay = 0, args = [] ):
          task = Task( action, loopdelay, initdelay, args )

          if loopdelay:
              self._tasks.append( task )
          else:
              task.start()


      def StartAllTasks( self ):
          for task in self._tasks:
              task.start()

      def StopAllTasks( self ):
          for task in self._tasks:
              print 'Stopping task', task
              task.stop()
              task.join(1)


if __name__ == '__main__':

    def timestamp( s ):
        print '%.2f : %s' % ( time.time(), s )

    def Task1():
        timestamp( 'Task1' )

    def Task2():
        timestamp( '\tTask2' )

    def Task3():
        timestamp( '\t\tTask3' )

    s = Scheduler()

    # -------- task - loopdelay - initdelay 
    s.AddTask( Task1,    0,        3,  args=(1,2)  )
    s.AddTask( Task2,    1.5,      0.25     )
    s.AddTask( Task3,    0.5,      0.05     )

    print s
    s.StartAllTasks()
    raw_input()
    s.StopAllTasks()
