function [time,quake_data,X] = quake_SAC2d ( quake_set, delta_t, f_lo,f_hi,seed)
% [ time, quake_data, X ] = quake_SAC2d ( quake_set, delta_t, f_lo, f_hi, seed )
%
% Generate an artificial (synthetic) earthquake ground motion record
% with a consistent acceleration, velocity, and displacemnt pulse 
% using ground motion parameters representative of a SAC ground motion set
%
%  Input Variable        Description
%  --------------         -----------
%    quake_set   one of ...
%                'nrfault'    near fault - LA 10 percent in 50 year
%                'la10in50'   LA 10 percent in 50 year (default)
%                'la2in50'    LA  2 percent in 50 year
%                'se10in50'   Seattle 10 percent in 50 year
%                'se2in50'    Seattle  2 percent in 50 year
%      delta_t   the time step constant, sec
%      f_lo      low  spectral frequency value (default = 0.10 Hz)
%      f_hi      high spectral frequency value (default = 10.0 Hz)
%      seed      a seed for the random phase generation
%
%  Output Variable        Description
%  --------------         -----------
%         time    : time record ...  ( time  = [1:P]' * delta_t; )
%     quake_data  : earthquake ground motion data ...  
%                   P rows, six columns 
%                   [ accelNS  velocNS  displNS  accelEW  velocEW  displEW ]
%            X    : vector of 13 ground motion parameters used in simulation
%                  [ VpNS  VpEW Tp Nc Tpk phi VrNS VrEW tau1 tau2 tau3 fg zg ]

%
% Henri Gavin, Civil and Environmental Engineering, Duke Univsersity, 
% Jul. 2007, Nov 2007, Mar 2008, Apr 2008

v = version; Octave = v(1)<'5';  % Octave test
if Octave
   randomizer = 'seed';                 % Octave
else
   randomizer = 'state';                % Matlab
end

 Plots   = 1;		% make Plots

% --- default values ---

  if nargin < 1, quake_set = 'la10in50'; end
  if nargin < 2, delta_t = 0.01; end
  if nargin < 3, f_lo = 0.10; end % minimum spectral frequency Hz
  if nargin < 4, f_hi = 10.0; end % maximum spectral frequency Hz
  if nargin > 4, rand (randomizer, seed); end

  % initialize random number generator

% generate a sample of ground motion parameters
 X = SAC_stats2d(quake_set,3);
 if strcmp(quake_set , 'nrfault'),  f_lo = 0.10; f_hi= 8.0; end
 if strcmp(quake_set , 'la10in50'), f_lo = 0.07; f_hi= 9.0; end
 if strcmp(quake_set , 'la2in50'),  f_lo = 0.07; f_hi= 9.0; end
 if strcmp(quake_set , 'se10in50'), f_lo = 0.10; f_hi=20.0; end
 if strcmp(quake_set , 'se2in50'),  f_lo = 0.10; f_hi=20.0; end

 format bank
 fprintf('   VpNS   VpEW     Tp     Nc    Tpk    phi    VrNS   VrEW     tau1   tau2   tau3  fg    zg \n');
 fprintf('%6.2f ', X(1:13)  );
 fprintf('\n');
 format


 VpNS = X( 1);		% pulse period, s
 VpEW = X( 2);		% pulse period, s
 Tp   = X( 3);		% pulse period, s
 Nc   = X( 4);		% number of cycles in pulse 
 Tpk  = X( 5);          % time of peak of the pulse, s
 phi  = X( 6);		% phase angle of the pulse, rad
 VrNS = X( 7);		% peak spectral velocity of the random motoin, cm/s
 VrEW = X( 8);		% peak spectral velocity of the random motoin, cm/s
 tau1 = X( 9);		% envelope rise time, s
 tau2 = X(10);		% envelope plateau time, s
 tau3 = X(11);		% envelope decay time, s
 fg   = X(12);		% central frequency, Hz
 zg   = X(13);		% damping ratio

 T0 = 5.0;                        % initial time of no motion
 P0 = floor(T0/delta_t);          % initial points of no motion
 P1 = floor(tau1/delta_t);	  % points in envelope rise
 P2 = floor(tau2/delta_t);	  % points in envelope plateau
 P3 = floor(tau3/delta_t);	  % points in envelope decay
 P  = max(P0+P1+P2+4*P3,60/delta_t); % total number of points in earthquake record
 envl  = [ [1:P0]*0 ( [1:P1]/P1 ).^2 ones(1,P2-1) exp(-( [P0+P1+P2:P] - P0-P1-P2 )/P3) ];

 Pe = length(envl);
 if Pe > P
    envl = envl(1:P);
 end
 if Pe < P
    envl = [ envl 0 ];
 end

 time  = [1:P]' * delta_t;

 NF   = 1024;			% number of discrete frequencies to sample-1
 NF   = max(1024,P/2);
 delta_f = ( f_hi - f_lo ) / (NF-1); 	% frequency increment
 freq  = [f_lo:delta_f:f_hi];  % spectral frequencies

 ampl  = zeros(1,NF);
 for k = 1:NF			% spectral spectral power
     ampl(k)  = ( 0 + (2*zg*freq(k)/fg)^2 ) / ... 
                ( (1-(freq(k)/fg)^2)^2 + (2*zg*freq(k)/fg)^2 );
 end

 for direction = 1:2		% direction loop --- 1: NS,  2: EW

     if direction == 1, Vp = X(1); else, Vp = X(2); end
     if direction == 1, Vr = X(7); else, Vr = X(8); end

     phase = 2*pi*rand(1,NF);	% uniformly distributed random phase
     accel = zeros(1,P);
     for k = 1:NF
      accel = accel + ...
              sqrt(4*ampl(k)*delta_f) * cos(2*pi*freq(k)*time' + phase(k) );
     end

     accel = ( envl .* accel )';		 % unscaled accel without pulse
     veloc = ftdsp(accel,1,f_lo,f_hi,1/delta_t); % unscaled veloc without pulse
     [Vm,idx] = max(abs(veloc)); 		 % uscaled peak veloc
     scale = Vr/Vm*sign(veloc(idx)); 		 % veloc scale factor 
     veloc = veloc' * scale;			 % scaled veloc without pulse
 
%    Tpk = idx*delta_t;
    
%    if Plots                 % PSD of accel without the pulse
%       nfft = 1024;
%       [S,f] = psd(accel,nfft,1/delta_t, hanning(nfft), nfft/2 );
%       if direction == 1, Sx = S; end
%       if direction == 2, Sy = S; end
%    end

     phi = 2*pi*rand;				% random phase of pulse
     [t,pulse] = pulseV(Vp,Tp,Nc,T0+Tpk,phi,P,delta_t);	% pulse generation
     if direction == 1, pulse_ns = pulse; end
     if direction == 2, pulse_ew = pulse; end
    
     veloc = veloc' + pulse(:,2);
     accel = ftdsp ( veloc,-1, 0.0,f_hi,1/delta_t);	% compute accel
     displ = cumtrapz(veloc)*delta_t;                   % compute displ

     if direction == 1
        quake_data_ns = [ accel veloc displ ];
     else
        quake_data_ew = [ accel veloc displ ];
     end

 end				% direction loop --- 0: NS,  1: EW

  quake_data = [ quake_data_ns  quake_data_ew ];


 if Plots	% --- plot the earthquake
   
  T = 45;       % maximum time displayed in the plots

% figure(7)
%  clf
%  semilogx( f(2:nfft/2), Sx(2:nfft/2)/max(Sx), ...
%            f(2:nfft/2), Sy(2:nfft/2)/max(Sy), ...
%            freq, ampl );
%  ylabel('normalized accel. power spectra')
%  xlabel('frequency, Hz')
%  axis( [ f_lo f_hi 0 1 ] )

   figure(8)
    clf
    subplot(121)
     plot ( quake_data_ew(:,3), quake_data_ns(:,3) )
      xlabel('displ EW, cm')
      ylabel('displ NS, cm')
      axis('equal')
    subplot(122)
     plot ( quake_data_ew(:,2), quake_data_ns(:,2) )
      xlabel('veloc EW, cm/s')
      ylabel('veloc NS, cm/s')
      axis('equal')

   figure(9) 
    clf
    subplot(321)
     plot( time,pulse_ns(:,1),'-r', time,quake_data_ns(:,1),'-b')
     ylabel('accel. cm/s/s')
     xlim ([ 1 T ])
    subplot(322)
     plot( time,pulse_ew(:,1),'-r', time,quake_data_ew(:,1),'-b')
     ylabel('accel. cm/s/s')
     xlim ([ 1 T ])
    subplot(323)
     plot( time, quake_data_ns(:,2)-pulse_ns(:,2),'-k', ...
           time, pulse_ns(:,2),'-r', ...
           time, quake_data_ns(:,2),'-b' );
     ylabel('veloc. cm/s')
     xlim ([ 1 T ])
    subplot(324)
     plot( time, quake_data_ew(:,2)-pulse_ew(:,2),'-k', ...
           time, pulse_ew(:,2),'-r', ...
           time, quake_data_ew(:,2),'-b' );
     ylabel('veloc. cm/s')
     xlim ([ 1 T ])
    subplot(325)
     plot( time,pulse_ns(:,3),'-r', time,quake_data_ns(:,3),'-b' )
     ylabel('displ. cm/s')
     xlim ([ 1 T ])
    subplot(326)
     plot( time,pulse_ew(:,3),'-r', time,quake_data_ew(:,3),'-b' )
     ylabel('displ. cm/s')
     xlim ([ 1 T ])

 end 	        % --- plot the earthquake

% -------------------------------------------------- QUAKE_SAC2D
