function y = ftdsp(u,ni,flo,fhi,sr)
% y = ftdsp(u,ni,flo,fhi,sr)
% band-pass filter and integrate a discrete-time signal, u 
%  u  : the discrete-time signals to be filtered/integrated, in column vectors
% ni  : the number of integrations (may be zero or negative for differentiation)
% flo : the  low frequency limit for the bandpass filter  ( >= 0 )
% fhi : the high frequency limit for the bandpass filter  ( <= sr/2 );
% sr  : the sample rate

% H.P. Gavin, Dept. Civil and Environ. Eng'g, Duke Univ., Jul. 2007

 [P,m] = size(u);
 if m > P, error('ftdsp: input series, u, should be in column vectors'); end

% de-trending and windowing the data can help with numerical accuracy 
 u  = detrend(u);		% detrend or base-line correction
 Pw = floor(P/20);		% number of window points
 w = [ 0.5*(1-cos(pi*[0:Pw]/Pw)) ones(1,P-2*Pw-2) 0.5*(1+cos(pi*[0:Pw]/Pw)) ]';
 u = u .* (w*ones(1,m)); 	% comment out this line for no windowing

 NF = 2 ^ ceil( log(P)/log(2) );	% use 2^n points for FFT calculations

 delta_f = sr/NF; 			% frequency resolution

 f = [ [0:NF/2] [-NF/2+1:-1] ]' * delta_f;  % frequency data

 kloP = max(floor( flo/delta_f) + 1, 1 );
 khiP = min(floor( fhi/delta_f) + 1, NF/2+1 );
 kloN = min( ceil(-flo/delta_f) + 1 + NF, NF );
 khiN = max( ceil(-fhi/delta_f) + 1 + NF, NF/2+2 );

 Nband_lo = round (abs(khiP-kloP)/10);	% low  frequency transition bandwidth
 Nband_hi = round (abs(khiP-kloP)/10);  % high frequency transition bandwidth
 if Nband_lo > kloP, Nband_lo = kloP+1; end
 if Nband_hi > khiP, Nband_hi = khiP+1; end

 H = zeros(NF,1);			% initialize filter transfer function
 H([kloP:khiP]) = 1;			% positive band pass frequencies
 H([khiN:kloN]) = 1;			% negative band pass frequencies

 if flo > delta_f
    for k = 0:Nband_lo			% taper in frequency domain
        H([ kloP+k kloN-k ]) = 0.5*(1-cos(k*pi/Nband_lo));
    end
 end
 if fhi < sr/2-delta_f
    for k = 0:Nband_hi			% taper in frequency domain
        H([ khiP-k khiN+k ]) = 0.5*(1-cos(k*pi/Nband_hi));
    end
 end

 ID = (i*2*pi*f).^(-ni);  ID(1) = 1;	% integration/differentiation filter

 U  = fft(u,NF);			% take the FFT of the real signal, u

 Y  = [ H.*ID*ones(1,m) ].*U;   % convolution with the filter transfer function

 y  = ifft(Y,NF);		% Inverse FFT 

 if ( ( max(norm(imag(y)') ./ norm(real(y)')) ) > 1e-4 )
	disp( norm(imag(y)') ./ norm(real(y)') )
	disp('ftdsp: uh-oh, the imaginary part should be practically zero');
 end

 y = real(y(1:P,:));		% retain only the original N data points
% ---------------------------------------------------------------------- FTDSP
