courses_list = ['algo-004', 'gametheory-003', 'ml-005', 'cs101', 'crypto-010', 'startup-001', 'nlp', 'datasci-001', 'machlearning-001', 'pgm-003', 'algo2-003', 'ml-003', 'cplusplus4c-002', 'algs4partII-002', 'algs4partI-003', 'sna-003', 'audio-001', 'introfinance-008', 'europe-002', 'statistics-003', 'algo-007', 'ntumltwo-001', 'compilers', 'basicwriting-005', 'algs4partII-003', 'name', 'images-2012-001', 'datascitoolbox-017', 'pgm', 'db', 'climatechange-001', 'gamification-003', 'textanalytics-001', 'hci', 'intrologic', 'automata', 'algo', 'modelthinking', 'hciucsd-005', 'gametheory', 'gamification-002', 'analyticalchem-001', 'crypto-preview', 'android-001', 'bizsociety-001', 'automata-002', 'datascitoolbox-014', 'steinmicro-002', 'criticalmanagement-001', 'introgalois-001', 'recsys-001', 'pythonlearn-005', 'networks-003', 'posa-002', 'eefun-001', 'design-002', 'globalhealthintro-003', 'linearopt-002', 'algo2-002', 'operations-002', 'eqp-003', 'hci-003', 'ntusym-003', 'mythology-002', 'votingfairdiv-001', 'strategy101-001', 'rationing-001', 'hci-2012-002', 'surveillance-001', 'molevol-001', 'compinvesting1-003', 'learning-001', 'ggp-003', 'ticyeducacion-002', 'ciencia-002', 'scanfilmtv-001', 'americanlaw-001', 'drugsandbrain-002', 'molevol-003', 'analyze-003', 'visualpercepbrain-002', 'oldglobe-001', 'aids-001', 'intrologic-004', 'ourenergyfuture-001', 'usefulgenetics-003', 'afp21stcentury-001', 'mobilecloud-001', 'algo-003', 'organalysis-003', 'experiments-001', 'genes-003', 'calcsing-2012-001', 'soulbeliefs-001', 'vaccines-003', 'spatialcomputing-001', 'operations-2012-001', 'gametheory-004']

for courses in courses_list:
	print "mkdir " + courses
	print 'cp CourseraSubtitle.py ./'  + courses
	print 'cp DownloadSubtitle.py ./'  + courses
	print 'cd ./'  + courses
	print "python CourseraSubtitle.py " + courses
	print "python CourseraSubtitle.py " + courses
	print "rm -f ./CourseraSubtitle.py *.pyc database.db ./DownloadSubtitle.py"
	print "cd .."