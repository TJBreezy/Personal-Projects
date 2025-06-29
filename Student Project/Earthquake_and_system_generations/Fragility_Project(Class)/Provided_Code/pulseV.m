function [time,pulse] = pulseV( Vp, Tp, Nc, Tpk, phi, P, delta_t)
% [TIME,PULSE] = PULSEV(Vp,Tp,Nc,Tpk,phi,P,delta_t)  
% Computes an earthquake-like acceleration, velocity, and displacemnt pulse 
%     INPUT                                                  DEFAULT
%   =========                                                =======
%       Vp   - max velocity of pulse                           1.0
%       Tp   - time period of pulse                            1.0
%       Nc   - number of cycles in pulse ... approximate       1.0
%       Tpk  - location of peak pulse in time axis             1.0
%       phi  - phase of the pulse ... between -pi and +pi      0
%       P    - number of points in the pulse record            1000
%       delta_t - time step value                              0.005
%
%   OUTPUT
%   ======
% The  first column of PULSE contains an 'acceleration' record.
% The second column of PULSE contains a    'velocity'   record.
% The  third column of PULSE contains a  'displacement' record.

Plots   = 0;	% 1: make plots,             0: don't
PSPlots = 0;	% 1: make PostScript plots,  0: don't

if nargin < 7,	delta_t = 0.005;end
if nargin < 6,	P       = 1000;	end
if nargin < 5,	phi     = 0;	end
if nargin < 4,	Tpk     = 1;	end
if nargin < 3,	Nc      = 1;	end
if nargin < 2,	Tp      = 1;	end
if nargin < 1,	Vp      = 1;	end

% v = version; Octave = v(1)<'5';  % Octave test

 time = [1:P]*delta_t;	

 ts = (time - Tpk)*2*pi/Tp/Nc;		              % scaled time

%veloc =  Vp * exp(-ts.^2/16) .* cos( Nc*ts );        % even pulse
%veloc =  Vp * exp(-ts.^2/16) .* sin( Nc*ts );        % odd  pulse
 veloc =  Vp * exp(-ts.^2/16) .* cos( Nc*ts - phi );  % even pulse if phi=0

 accel = [ veloc(:,2)-veloc(:,1) 0.5*[ veloc(:,3:P) - veloc(:,1:P-2) ] veloc(:,P)-veloc(:,P-1) ] / delta_t;

 displ = cumtrapz(veloc)*delta_t;

 pulse = [ accel'  veloc'  displ' ];

if Plots % plot the pulse

   figure(8); ylabel(''); title(''); axis;
   xlabel('time, s')
   if ~PSPlots, subplot(3,1,1); end
    plot (time,accel);
    ylabel('accel, cm/s/s')
%   if PSPlots, saveplot('pulseA.ps',1,0.4,1,14,2); end
   if ~PSPlots, subplot(3,1,2); end
    plot (time,veloc);
    ylabel('veloc, cm/s')
%   if PSPlots, saveplot('pulseV.ps',1,0.4,1,14,2); end
   if ~PSPlots, subplot(3,1,3); end
    plot (time,displ);
    ylabel('displ, cm')
%   if PSPlots, saveplot('pulseD.ps',1,0.4,1,14,2); end
       
    xlabel(''); ylabel(''); axis;

end
% endfunction # ------------------------------------------------------- PULSEV 
