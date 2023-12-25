mkdir "./deploy"
robocopy ./control ./deploy /e
pscp -r -pw quadruped123 ./deploy easternspork@192.168.1.124:/home/easternspork/