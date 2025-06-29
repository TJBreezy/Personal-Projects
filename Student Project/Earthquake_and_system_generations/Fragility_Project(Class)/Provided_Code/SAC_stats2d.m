function [ X, Ex, Vx, Cz ]  = SAC_stats2d(quake_set,N)
% [ X, Ex, Vx, Cz ]  = SAC_stats2d(quake_set,N)
% Return ground motion paramters and parameter statistics for a 
% particular uni-directional SAC earthquake scenario
% http://nisee.berkeley.edu/data/strong_motion/sacsteel/ground_motions.html
%
%     INPUT      DESCRIPTION
%    quake_set   one of ...
%                'nrfault'  LA near fault ground motion
%                'la10in50'   LA 10 percent in 50 year
%                'la2in50'    LA  2 percent in 50 year
%                'se10in50'   Seattle 10 percent in 50 year
%                'se2in50'    Seattle  2 percent in 50 year
%
%     N          maximum allowable variability in Vp, Vr, and Tp  ... 3 or 4
%                X will be less than Ex + N * sqrt(Vx);
%
%    OUTPUT      DESCRIPTION
%     X          ground motion parameters
%     Ex         ground motion parameter mean values
%     Vx         ground motion parameter variances
%     Cz         ground motion parameter correlation matrix 
%                for standardized random variables
%
%  where
%
%  X(1)  ... Vp  peak velocity of coherent pulse, cm/s   NS
%  X(2)  ... Vp  peak velocity of coherent pulse, cm/s   EW
%  X(3)  ... Tp  period of coherent pulse, s
%  X(4)  ... Nc  cycles in coherent pulse
%  X(5)  ... Tpk time to the peak of the pulse
%  X(6)  ... phi phase angle of the pulse
%  X(7)  ... Vr peak velocity of incoherent ground motion, cm/s  NS
%  X(8)  ... Vr peak velocity of incoherent ground motion, cm/s  EW
%  X(9)  ... Tau1 envelope rise time, s
%  X(10) ... Tau2 constant time, s
%  X(11) ... Tau3 envelope decay time, s
%  X(12) ... power spectrum central frequency, Hz
%  X(13) ... power spectrum bandwidth factor,
%
% Ground motion parameters are generated according to the
% lognormal probability distribution function.
%
% A default case is also provided in which the ground motion paramters
% are similar to those of la10in50, but without any cross-correlation.
%
% (Tp   -  0.8) is lognormal-distributed with mean Ex(3) and variance Vx(3)
% (Nc   -  0.5) is lognormal-distributed with mean Ex(4) and variance Vx(4)
% (phi  + 2*pi) is lognormal-distributed with mean Ex(6) and variance Vx(6)
% (Vr   - 10.0) is lognormal-distributed with mean Ex(7) and variance Vx(7) NS
% (Vr   - 10.0) is lognormal-distributed with mean Ex(8) and variance Vx(8) EW
% (Tau1 -  1.0) is lognormal-distributed with mean Ex(9) and variance Vx(9)
% (Tau3 -  1.0) is lognormal-distributed with mean Ex(11) and variance Vx(11)

if strcmp(quake_set,'nrfault')

% original fit values - 2D
%       VpNS   VpEW   Tp   Nc    Tpk  phi     VrNS   VrEW   tau1 tau2  tau3  fg   zg
%Ex = [ 90.83  90.83   1.58 0.88  5.04 7.12   57.04  57.04   4.02 0.48  4.08 0.76 1.41];
%Vx = [5490.69 5490.69 1.13 0.43 10.44 4.31 1092.84 1092.84 13.38 0.57  5.34 0.01 0.02]; 

% response spectrum compatible - 2D
%       VpNS   VpEW   Tp   Nc    Tpk  phi     VrNS   VrEW   tau1 tau2  tau3   fg  zg
 Ex = [ 100    100     1.1  0.9   5.0  6.28    70      70    4.0  0.5   4.1   0.5 1.0 ];
 Vx = [  40     40     1.2   0     0    0      35      35     0    0     0    0.2  0].^2; 

%        VpNS   VpEW    Tp    VrNS   VrEW
Cz5 = [  1.00   0.35  -0.51   0.20   0.10  ;	% VpNS
         0.35   1.00  -0.08  -0.03  -0.04  ;	% VpEW
        -0.51  -0.08   1.00  -0.11  -0.09  ;	% Tp
         0.20  -0.03  -0.11   1.00   0.68  ;	% VrNS
         0.10  -0.04  -0.09   0.68   1.00  ];	% VrEW


elseif strcmp(quake_set,'la10in50')

% original fit values - 2D
%       VpNS   VpEW   Tp   Nc    Tpk  phi     VrNS   VrEW   tau1 tau2  tau3  fg   zg
%Ex = [ 45.28   45.28  1.85 0.80  4.97 6.48    34.83  34.83  3.77 0.14  4.48 0.78 1.76];
%Vx = [ 520.25 520.25  1.57 0.67 11.05 3.10   281.24 281.24  7.25 0.02  9.59 0.01 0.02];

% response spectrum compatible - 2D
%       VpNS   VpEW   Tp   Nc    Tpk  phi     VrNS   VrEW   tau1 tau2  tau3  fg   zg
 Ex = [  15     15     5.0  0.8   5.0  6.28    60     60     3.7  0.2   4.5  1.0  1.8 ];
 Vx = [  50     50     0.5   0     0    0      30     30      0    0     0   0.1   0].^2;


%        VpNS   VpEW    Tp    VrNS   VrEW
Cz5 = [  1.00   0.52  -0.26  -0.17   0.03   ;	% VpNS
         0.52   1.00  -0.51   0.01   0.33   ;	% VpEW
        -0.26  -0.51   1.00  -0.05  -0.39   ;	% Tp
        -0.17   0.01  -0.05   1.00   0.70   ;	% VrNS
         0.03   0.33  -0.39   0.70   1.00   ];	% VrEW

elseif strcmp(quake_set,'la2in50')

% original fit values - 2D
%       VpNS   VpEW   Tp   Nc    Tpk  phi     VrNS   VrEW   tau1 tau2  tau3  fg   zg
%Ex = [ 99.99  99.99   1.72 0.64  4.81 6.26   74.88   74.88  4.46 0.53  3.81 0.73 1.36 ];
%Vx = [2268.06 2259.06 0.89 0.22 12.16 6.05 1006.38 1006.38 13.27 0.59  3.78 0.01 0.02 ];

% response spectrum compatible - 2D
%       VpNS   VpEW   Tp   Nc    Tpk  phi     VrNS   VrEW   tau1 tau2  tau3  fg   zg
 Ex = [  50     50     1.7  0.7   4.8  6.28    120    120     4.5  0.5   3.8 0.7  1.2 ];
 Vx = [  60     60     0.7   0     0    0       40     40      0    0     0  0.1   0].^2;


%        VpNS   VpEW    Tp    VrNS   VrEW
Cz5 = [  1.00   0.75  -0.58  -0.08  -0.25 ;	% VpNS
         0.75   1.00  -0.62  -0.65  -0.68 ;	% VpEW
        -0.58  -0.62   1.00   0.32   0.43 ;	% Tp
        -0.08  -0.65   0.32   1.00   0.84 ;	% VrNS
        -0.25  -0.68   0.43   0.84   1.00 ];	% VrEW


elseif strcmp(quake_set,'se10in50')

% original fit values - 2D
%       VpNS   VpEW   Tp   Nc    Tpk  phi     VrNS   VrEW   tau1 tau2  tau3  fg   zg
%Ex = [ 11.60  11.60   1.75 0.84  6.11 7.44   22.22  22.22  12.25 0.14 10.40 1.33 0.82 ];
%Vx = [143.40 143.40   0.42 0.09  6.08 2.77  141.76 141.76 170.02 0.01 68.48 0.02 0.01 ];

% response spectrum compatible - 2D
%       VpNS   VpEW   Tp   Nc    Tpk  phi     VrNS   VrEW   tau1 tau2  tau3  fg   zg
 Ex = [ 10    10      2.1   0.8   6.1  6.28     25     25    12.2  0.2  10.4 1.8  1.7 ];
 Vx = [ 20    20      0.8    0     0    0       30     30      0    0     0  0.2   0].^2;

%        VpNS   VpEW    Tp    VrNS   VrEW
Cz5 = [  1.00   0.82   0.08  -0.46  -0.61  ;	% VpNS
         0.82   1.00  -0.05  -0.56  -0.38  ;	% VpEW
         0.08  -0.05   1.00   0.01  -0.27  ;	% Tp
        -0.46  -0.56   0.01   1.00   0.44  ;	% VrNS
        -0.61  -0.38  -0.27   0.44   1.00  ];	% VrEW


elseif strcmp(quake_set,'se2in50')

% original fit values - 2D
%       VpNS   VpEW   Tp   Nc    Tpk  phi     VrNS   VrEW   tau1 tau2  tau3  fg   zg
%Ex = [ 34.13  34.13   1.82 1.17  6.61 7.36   63.76  63.76  15.66 0.13 10.62 1.15 0.81 ];
%Vx = [1345.70 1345.70 1.10 0.35 11.33 3.45  682.06 682.06 214.05 0.02 52.39 0.02 0.007];

% response spectrum compatible - 2D
%       VpNS   VpEW   Tp   Nc    Tpk  phi     VrNS   VrEW   tau1 tau2  tau3  fg   zg
 Ex = [  40     40    1.0   1.2   6.6  6.28     60     60    15.7 0.20  10.6 1.7  1.7 ];
 Vx = [  12     12    1.0    0     0    0       50     50      0   0      0  0.2   0].^2;


%        VpNS   VpEW    Tp    VrNS   VrEW
Cz5 = [  1.00   0.94  -0.60  -0.43  -0.23  ;	% VpNS
         0.94   1.00  -0.62  -0.48  -0.16  ;	% VpNS
        -0.60  -0.62   1.00  -0.18  -0.18  ;	% NS
        -0.43  -0.48  -0.18   1.00   0.55  ;	% VrNS
        -0.23  -0.16  -0.18   0.55   1.00  ];	% VrNS


else

% default values

end

v = [ 1 2 3 7 8 ];                 % list of random variables

Cz = eye(13);
Cz(v,v) = Cz5;

ok = 0;
while ~ok                          % loop until a suitable set of R.V's found

% generate correlated standard normal random variables
     Zc =  randn(1,13) * chol(Cz);    % correlated Gaussean random variables
%    Zc =  randn(1,13);               % uncorrelated Gaussean r.v's
% lognormal random variable
     COV  = sqrt(Vx) ./ Ex;         % coefficient of variation of X
     Vlnx = log(COV.^2 + 1);        % Variance of log(X)
     X = Ex .* exp( -0.5 * Vlnx + Zc .* sqrt(Vlnx) ); % correlated lognormal

     X(3)  = X(3)  + 0.8;            % add 0.8 s     offset to Tp
     X(4)  = X(4)  + 0.5;            % add 0.5 cycle offset to Nc
     X(6)  = X(6)  - 2*pi;           % subtract 2pi  offset from phi
     X(7)  = X(7)  + 10.0;           % add 10 cm/s   offset to Vr NS
     X(8)  = X(8)  + 10.0;           % add 10 cm/s   offset to Vr EW
     X(9)  = X(9)  +  1.0;           % add 1.0 s     offset to Tau1
     X(11) = X(11) +  1.0;           % add 1.0 s     offset to Tau3

% check for extremely large random variables
  
      if ( X(1) < Ex(1) + N*sqrt(Vx(1)) && ...       % Vp not too big
           X(2) < Ex(2) + N*sqrt(Vx(2)) && ...       % Vp not too big
           X(3) < Ex(3) + N*sqrt(Vx(2)) + 0.8 && ... % Tp not too big
           X(6) < Ex(6) + N*sqrt(Vx(6)) && ...       % Vr not too big
           X(7) < Ex(7) + N*sqrt(Vx(7)) )            % Vr not too big
           ok = 1;                                 % this set of R.V's is OK  
      end 
 
% adjust Tpk and tau_3 for pulse to arrive at an appropriate time
     X(5)  = min(X(5),(X(9)+X(10)+X(11))/4); % pulse does not arrive too late
     X(5)  = max(X(5),X(9)+X(3)*X(4)/2);     % pulse does not arrive too early
     X(11) = max(X(11),X(3)*X(4)-X(9));      % duration must include the pulse

end

return

%  X(1)  ... Vp  peak velocity of coherent pulse, cm/s   NS
%  X(2)  ... Vp  peak velocity of coherent pulse, cm/s   EW
%  X(3)  ... Tp  period of coherent pulse, s
%  X(4)  ... Nc  cycles in coherent pulse
%  X(5)  ... Tpk time to the peak of the pulse
%  X(6)  ... phi phase angle of the pulse
%  X(7)  ... Vr peak velocity of incoherent ground motion, cm/s  NS
%  X(8)  ... Vr peak velocity of incoherent ground motion, cm/s  EW
%  X(9)  ... Tau1 envelope rise time, s
%  X(10) ... Tau2 constant time, s
%  X(11) ... Tau3 envelope decay time, s
%  X(12) ... power spectrum central frequency, Hz
%  X(13) ... power spectrum bandwidth factor,

% -----------------------------------------------------------------------
