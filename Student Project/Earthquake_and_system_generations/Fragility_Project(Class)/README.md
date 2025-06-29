# Project Structure and Workflow

Explanation of the project structure and how to run the different parts. 

# How to Run:
Save each code block into its respective .m file within the folder structure described earlier.
Place the provided .m files (ftdsp.m, etc.) into the Provided_Code/ folder.
Open MATLAB, navigate to the Main Project Folder.
Add the subfolders to the path: addpath(genpath(pwd));
Run Run_Generate_GMs; (This might take a few minutes depending on Num_GMs).
Run Run_IDA_Analysis; (This will take the longest time, potentially hours, especially without parallel processing).
Run Run_Fit_Fragility; (This should be relatively quick).
This will generate the ground motions, perform the IDA, fit the fragility curves using MLE, save the parameters, and produce plots comparing the linear and nonlinear fragility curves. Remember to check the example damage state thresholds and replace them with appropriate values from FEMA P-58 for your assumed structural system type.


#IDA Curves
% In the MATLAB command window or a new script:
    addpath(genpath(pwd)); % Make sure paths are set
    load('Results/IDA_Results.mat'); % Load the results
    Plot_IDA_Curves(IDA_Results);     % Call the plotting function