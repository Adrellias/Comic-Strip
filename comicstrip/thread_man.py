'''
  Author: <adrellias@gmail.com>

  This module handles the creation of threads
  For once off and scheduled continues looping jobs

  Originaly Based on:
  http://code.activestate.com/recipes/114644/
  and Sickbeards scheduler:
  https://github.com/SickBeard-Team/SickBeard/blob/develop/sickbeard/scheduler.py
'''

import time
import datetime
import threading


class Task(threading.Thread):

    def __init__(self, action, cycleTime, runImmediately, *args):
        ''' Initiate thread startup '''
        self._action = action
        self._cycleTime = cycleTime
        self._args = args[0]
        self._running = 1

        if runImmediately:
            self._lastRun = datetime.datetime.fromordinal(1)
        else:
            self._lastRun = datetime.datetime.now()

        threading.Thread.__init__(self)

    def __repr__(self):
        ''' Return the options we passed '''
        return '%s %s %s' % (
            self._action, self._cycleTime, self._lastRun)

    def run(self):
        ''' Run the function we want '''

        while True:
            currentTime = datetime.datetime.now()

            if currentTime - self._lastRun > self._cycleTime:
               self._lastRun = currentTime
               try:
                   self._action()

               except Exception, e:
                   print "Exception generated in thread %s" % (ex(e))

            if not self._running:
                return

            time.sleep(1)

    def stop(self):
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
              rep += '%s\n' % repr(task)
          return rep

      def AddTask(self, action, cycleTime=datetime.timedelta(minutes=10), runImmediately=True, args=None):
          task = Task( action, cycleTime, runImmediately, args )

          if cycleTime:
              self._tasks.append(task)
          else:
              task.start()


      def StartAllTasks(self):
          for task in self._tasks:
              task.start()

      def StopAllTasks(self):
          for task in self._tasks:
              print 'Stopping task', task
              task.stop()
              task.join(1)

if __name__ == '__main__':

    def timestamp( s ):
        print '%.2f : %s\r' % ( time.time(), s )

    def Task1():
        timestamp('Task1')

    def Task2():
        timestamp('\tTask2')

    def Task3():
        timestamp('\t\tTask3')

    s = Scheduler()

    # -------- task - cycleTime - initdelay
    s.AddTask( Task1,    datetime.timedelta(milliseconds=1))
    s.AddTask( Task2,    datetime.timedelta(milliseconds=1))
    s.AddTask( Task3,    datetime.timedelta(milliseconds=1))

    print s
    s.StartAllTasks()
    raw_input()
    s.StopAllTasks()
