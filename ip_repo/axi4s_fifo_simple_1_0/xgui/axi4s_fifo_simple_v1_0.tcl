# Definitional proc to organize widgets for parameters.
proc init_gui { IPINST } {
  ipgui::add_param $IPINST -name "Component_Name"
  #Adding Page
  set Page_0 [ipgui::add_page $IPINST -name "Page 0"]
  ipgui::add_param $IPINST -name "C_S00_AXIS_TDATA_WIDTH" -parent ${Page_0} -widget comboBox
  ipgui::add_param $IPINST -name "C_S00_AXI_DATA_WIDTH" -parent ${Page_0} -widget comboBox
  ipgui::add_param $IPINST -name "C_S00_AXI_ADDR_WIDTH" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_S00_AXI_BASEADDR" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_S00_AXI_HIGHADDR" -parent ${Page_0}

  ipgui::add_param $IPINST -name "G_FIFO_DEPTH"
  ipgui::add_param $IPINST -name "G_FIFO_TYPE"
  set G_FIFO_CASCADE_HEIGHT [ipgui::add_param $IPINST -name "G_FIFO_CASCADE_HEIGHT"]
  set_property tooltip {FIFO cascade height} ${G_FIFO_CASCADE_HEIGHT}
  set G_FIFO_READ_LATENCY [ipgui::add_param $IPINST -name "G_FIFO_READ_LATENCY"]
  set_property tooltip {FIFO read latency} ${G_FIFO_READ_LATENCY}

}

proc update_PARAM_VALUE.G_FIFO_CASCADE_HEIGHT { PARAM_VALUE.G_FIFO_CASCADE_HEIGHT } {
	# Procedure called to update G_FIFO_CASCADE_HEIGHT when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.G_FIFO_CASCADE_HEIGHT { PARAM_VALUE.G_FIFO_CASCADE_HEIGHT } {
	# Procedure called to validate G_FIFO_CASCADE_HEIGHT
	return true
}

proc update_PARAM_VALUE.G_FIFO_DEPTH { PARAM_VALUE.G_FIFO_DEPTH } {
	# Procedure called to update G_FIFO_DEPTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.G_FIFO_DEPTH { PARAM_VALUE.G_FIFO_DEPTH } {
	# Procedure called to validate G_FIFO_DEPTH
	return true
}

proc update_PARAM_VALUE.G_FIFO_READ_LATENCY { PARAM_VALUE.G_FIFO_READ_LATENCY } {
	# Procedure called to update G_FIFO_READ_LATENCY when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.G_FIFO_READ_LATENCY { PARAM_VALUE.G_FIFO_READ_LATENCY } {
	# Procedure called to validate G_FIFO_READ_LATENCY
	return true
}

proc update_PARAM_VALUE.G_FIFO_TYPE { PARAM_VALUE.G_FIFO_TYPE } {
	# Procedure called to update G_FIFO_TYPE when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.G_FIFO_TYPE { PARAM_VALUE.G_FIFO_TYPE } {
	# Procedure called to validate G_FIFO_TYPE
	return true
}

proc update_PARAM_VALUE.C_S00_AXIS_TDATA_WIDTH { PARAM_VALUE.C_S00_AXIS_TDATA_WIDTH } {
	# Procedure called to update C_S00_AXIS_TDATA_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S00_AXIS_TDATA_WIDTH { PARAM_VALUE.C_S00_AXIS_TDATA_WIDTH } {
	# Procedure called to validate C_S00_AXIS_TDATA_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S00_AXI_DATA_WIDTH { PARAM_VALUE.C_S00_AXI_DATA_WIDTH } {
	# Procedure called to update C_S00_AXI_DATA_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S00_AXI_DATA_WIDTH { PARAM_VALUE.C_S00_AXI_DATA_WIDTH } {
	# Procedure called to validate C_S00_AXI_DATA_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S00_AXI_ADDR_WIDTH { PARAM_VALUE.C_S00_AXI_ADDR_WIDTH } {
	# Procedure called to update C_S00_AXI_ADDR_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S00_AXI_ADDR_WIDTH { PARAM_VALUE.C_S00_AXI_ADDR_WIDTH } {
	# Procedure called to validate C_S00_AXI_ADDR_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S00_AXI_BASEADDR { PARAM_VALUE.C_S00_AXI_BASEADDR } {
	# Procedure called to update C_S00_AXI_BASEADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S00_AXI_BASEADDR { PARAM_VALUE.C_S00_AXI_BASEADDR } {
	# Procedure called to validate C_S00_AXI_BASEADDR
	return true
}

proc update_PARAM_VALUE.C_S00_AXI_HIGHADDR { PARAM_VALUE.C_S00_AXI_HIGHADDR } {
	# Procedure called to update C_S00_AXI_HIGHADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S00_AXI_HIGHADDR { PARAM_VALUE.C_S00_AXI_HIGHADDR } {
	# Procedure called to validate C_S00_AXI_HIGHADDR
	return true
}


proc update_MODELPARAM_VALUE.C_S00_AXIS_TDATA_WIDTH { MODELPARAM_VALUE.C_S00_AXIS_TDATA_WIDTH PARAM_VALUE.C_S00_AXIS_TDATA_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S00_AXIS_TDATA_WIDTH}] ${MODELPARAM_VALUE.C_S00_AXIS_TDATA_WIDTH}
}

proc update_MODELPARAM_VALUE.C_S00_AXI_DATA_WIDTH { MODELPARAM_VALUE.C_S00_AXI_DATA_WIDTH PARAM_VALUE.C_S00_AXI_DATA_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S00_AXI_DATA_WIDTH}] ${MODELPARAM_VALUE.C_S00_AXI_DATA_WIDTH}
}

proc update_MODELPARAM_VALUE.C_S00_AXI_ADDR_WIDTH { MODELPARAM_VALUE.C_S00_AXI_ADDR_WIDTH PARAM_VALUE.C_S00_AXI_ADDR_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S00_AXI_ADDR_WIDTH}] ${MODELPARAM_VALUE.C_S00_AXI_ADDR_WIDTH}
}

proc update_MODELPARAM_VALUE.G_FIFO_DEPTH { MODELPARAM_VALUE.G_FIFO_DEPTH PARAM_VALUE.G_FIFO_DEPTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.G_FIFO_DEPTH}] ${MODELPARAM_VALUE.G_FIFO_DEPTH}
}

proc update_MODELPARAM_VALUE.G_FIFO_TYPE { MODELPARAM_VALUE.G_FIFO_TYPE PARAM_VALUE.G_FIFO_TYPE } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.G_FIFO_TYPE}] ${MODELPARAM_VALUE.G_FIFO_TYPE}
}

proc update_MODELPARAM_VALUE.G_FIFO_CASCADE_HEIGHT { MODELPARAM_VALUE.G_FIFO_CASCADE_HEIGHT PARAM_VALUE.G_FIFO_CASCADE_HEIGHT } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.G_FIFO_CASCADE_HEIGHT}] ${MODELPARAM_VALUE.G_FIFO_CASCADE_HEIGHT}
}

proc update_MODELPARAM_VALUE.G_FIFO_READ_LATENCY { MODELPARAM_VALUE.G_FIFO_READ_LATENCY PARAM_VALUE.G_FIFO_READ_LATENCY } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.G_FIFO_READ_LATENCY}] ${MODELPARAM_VALUE.G_FIFO_READ_LATENCY}
}

