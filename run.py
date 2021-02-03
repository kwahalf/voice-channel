import server
import plac

def run_script_main():
  plac.call(server.main)

if __name__ == '__main__':
    run_script_main()