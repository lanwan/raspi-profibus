#!/usr/bin/env python3
#
# Simple pyprofibus example
#
# This example initializes an ET-200S slave, reads input
# data and writes the data back to the module.
#
# The hardware configuration is as follows:
#
#   v--------------v----------v----------v----------v----------v
#   |     IM 151-1 | PM-E     | 2 DO     | 2 DO     | 4 DI     |
#   |     STANDARD | DC24V    | DC24V/2A | DC24V/2A | DC24V    |
#   |              |          |          |          |          |
#   |              |          |          |          |          |
#   | ET 200S      |          |          |          |          |
#   |              |          |          |          |          |
#   |              |          |          |          |          |
#   |       6ES7   | 6ES7     | 6ES7     | 6ES7     | 6ES7     |
#   |       151-   | 138-     | 132-     | 132-     | 131-     |
#   |       1AA04- | 4CA01-   | 4BB30-   | 4BB30-   | 4BD01-   |
#   |       0AB0   | 0AA0     | 0AA0     | 0AA0     | 0AA0     |
#   ^--------------^----------^----------^----------^----------^
#

from pyprofibus.dp_master import *


# Enable verbose debug messages?
debug = True

# Create a PHY (layer 1) interface object
phy = CpPhy(debug=debug)

# Create a DP class 1 master with DP address 1
master = DPM1(phy = phy,
	      masterAddr = 1,
	      debug = debug)

# Create a slave description for an ET-200S.
# The ET-200S has got the DP address 8 set via DIP-switches.
et200s = DpSlaveDesc(identNumber = 0x806A,
		     slaveAddr = 8,
		     inputAddressRangeSize = 1,
		     outputAddressRangeSize = 2)

# Create Chk_Cfg telegram elements
for elem in (DpCfgDataElement(0),	# PM-E module
	     DpCfgDataElement(0x20),	# 2-DO module
	     DpCfgDataElement(0x20),	# 2-DO module
	     DpCfgDataElement(0x10)):	# 4-DI module
	et200s.chkCfgTelegram.addCfgDataElement(elem)

# Set User_Prm_Data
et200s.setPrmTelegram.addUserPrmData([0x11 | 0x40])

# Set various standard parameters
et200s.setSyncMode(True)		# Sync-mode supported
et200s.setFreezeMode(True)		# Freeze-mode supported
et200s.setGroupMask(1)			# Group-ident 1
et200s.setWatchdog(5000)		# Watchdog: 5 seconds

# Register the ET-200S slave at the DPM
master.addSlave(et200s)

try:
	# Initialize the DPM and all registered slaves
	master.initialize()
	print("Initialization finished. Running Data_Exchange...")

	# Cyclically run Data_Exchange.
	# 4 input bits from the 4-DI module are copied to
	# the two 2-DO modules.
	inData = 0
	while 1:
		outData = [inData & 3, (inData >> 2) & 3]
		inData = master.dataExchange(da = et200s.slaveAddr,
					     outData = outData)
		inData = inData[0] if inData else 0
except:
	print("Terminating.")
	master.destroy()
	raise
