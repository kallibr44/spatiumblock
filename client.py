import json,os,sys,db
try:
  import readline
except ImportError:
  import pyreadline as readline

def init():
    try:
        db.init()
        print("Database loaded!")
    except:
        print("Error loading database. Please, reinstall client.")

def main():

 pass


if __name__ == '__main__':
    init()