import games
import parity_progress_measures
import energy_progress_measures
import energy_progress_measures_fast # second implementation
import parity_executions
import energy_executions
import energy_executions_fast # second implementation
import trees
import util
import transcript

ex=1

if(ex==1):
    ###############
    ## EXAMPLE 1 ## (showing how to draw execution)
    ###############

    print("EXAMPLE 1")
    print("Compares the speed of the new implementation to the previous one")
    
    # generate a random energy game of size 100 and degree 2 (this is default)
    # and with weights up to 100
    g = games.game.generate_random(100,100,degree=2,typ="energy")
    g = g.boost_weights_to_remove_null_cycles()
    
    # initialize execution with timeout of 10 seconds
    exec=energy_executions_fast.execution(g,10)

    # rune snare_update algorithm (this is FVI). We enable the option that
    # saves the transcript (this makes the algorithm much slower, but 
    # allows to visual it afterwards)
    exec.snare_update(write_transcript=False)

    # we print some basic information in the console (runtime etc) 
    exec.printinfos()
    
    # we print the solution
    print(exec.solution)

    # initialize execution with timeout of 10 seconds
    exec=energy_executions.execution(g,10)

    # rune snare_update algorithm (this is FVI). We enable the option that
    # saves the transcript (this makes the algorithm much slower, but 
    # allows to visual it afterwards)
    exec.snare_update(player=1, write_transcript=False)

    # we print some basic information in the console (runtime etc) 
    exec.printinfos()
    
    # we print the solution
    print(exec.solution)

if(ex==2):
    print("\n \nEXAMPLE 2")

    ###############
    ## EXAMPLE 2 ## (showing difference between parity and energy versions of the algorithms)
    ###############

    # generate a random parity game of size 10 000 and degree 2
    # and with priorities up to 10 000
    g=games.game.generate_random(10000,10000, typ = "parity")

    # first make an execution the algorithm with timeout 30 sec
    exec=energy_executions.execution(g,30)

    # run the parity game version of the algorithm
    exec.snare_update(alternating=True)

    # print information
    exec.printinfos()

    # now transform g into an energy game. This takes some time...
    g_en=g.to_energy()
    print("done transforming into an energy game")

    # initialize execution with timeout of 30 seconds
    exec=energy_executions.execution(g_en,30)

    # run alternating algorithm
    exec.snare_update(alternating=True)

    # print information
    exec.printinfos()



if(ex==3):
    ###############
    ## EXAMPLE 3 ## (showing how to import a game from a file)
    ###############

    # import game from file
    g = games.game.from_file("instances/instance1")

    exec=energy_executions.execution(g,10)
    exec.snare_update(write_transcript=True)
    exec.printinfos()
    exec.draw_transcript(filename="drawings/test1/")
