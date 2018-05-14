
# Efficient Annotation of Scalar Labels (EASL)

Last update: May 14, 2018

[link to the paper (in preparation)]()


- - - 
## Pre-requisites

- Python 3.x
- numpy (`pip install numpy`)

## Procedure
1. Create your project by `sh create_project.sh YOUR_PROJECT_NAME` 

    Let's assume our project name is `political`.
    
    (e.g., `sh create_project.sh political`)
    
1. Prepare data (csv file) in `./experiments/political/XYZ.csv`
    
    Your data should be formatted in a csv file, consisting of (at least) the columns of `id, sent`.
    
             e.g., 
             id,sent
             1,obama is a legend in his own mind
             2,conservatives are racists
             3,cruz is correct
             4,romney is president
             5,obama thinks there are 57 states
             ...
       
    Let's assume the file name is `political.csv`
    
    Note: You can add additional columns. For example, if you want to annotate on a pair of sentences such as premise and hypothesis, the columns will look like `id, premise, hypothesis`)
    
    Run `python initialize.py ./experiments/political/political.csv` to set initial parameters (`alpha, beta, mu, sigma`)

    The result csv file (`political_0.csv`) should be as follows. 
    
         e.g., 
         id,sent,alpha,beta,mu,sigma
         1,obama is a legend in his own mind,1,1,0.5,0.0833
         2,conservatives are racists,1,1,0.5,0.0833
         3,cruz is correct,1,1,0.5,0.0833
         4,romney is president,1,1,0.5,0.0833
         5,obama thinks there are 57 states,1,1,0.5,0.0833
         ...
       
    It has additional columns: `alpha, beta, mu, sigma`.
    
    In this example, we place the file at `./experiments/political/political_0.csv`.
    
    Prepare your HIT template in `./templates/political/`
    
    See an example at `./templates/political/template_political.html`.
    
    Now, we are ready to start annotation with EASL!

1. Generate HITs

    We generate our HITs by running the following command. 
    
        python main.py --operation generate --model ./experiments/political/political_0.csv --hits 25

    This generates `political_hit_1.csv` that has 25 HITs. 
    
    The number of HITs (per iteration) should depend on your data size. (See `python main.py --help` for more details.)
    
1. Publish the HITs (with the template file.)

1. Collect the result and name it `./experiments/political/political_result_1.csv`.

1. Update the model

        python main.py --operation update --model ./experiments/political/political_0.csv

    This takes `political_0.csv`, `political_result_1.csv`, and then generate `political_1.csv`.
    
1. Go back to the step 3 (Generate HITs) and iterate the procedure. 

    (e.g., If this is the first iteration with `political_0.csv`, use `political_1.csv` to generate HITs in the next iteration.)

