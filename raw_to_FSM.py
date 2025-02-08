from collections import defaultdict

exit_reasons = {
	0: "EXCEPTION_NMI",
	1: "EXTERNAL_INTERRUPT",
	2: "TRIPLE_FAULT",
	3: "INIT_SIGNAL",
	4: "SIPI_SIGNAL",
	7: "INTERRUPT_WINDOW",
	8: "NMI_WINDOW",
	9: "TASK_SWITCH",
	10: "CPUID",
	12: "HLT",
	13: "INVD",
	14: "INVLPG",
	15: "RDPMC",
	16: "RDTSC",
	18: "VMCALL",
	19: "VMCLEAR",
	20: "VMLAUNCH",
	21: "VMPTRLD",
	22: "VMPTRST",
	23: "VMREAD",
	24: "VMRESUME",
	25: "VMWRITE",
	26: "VMOFF",
	27: "VMON",
	28: "CR_ACCESS",
	29: "DR_ACCESS",
	30: "IO_INSTRUCTION",
	31: "MSR_READ",
	32: "MSR_WRITE",
	33: "INVALID_STATE",
	34: "MSR_LOAD_FAIL",
	36: "MWAIT_INSTRUCTION",
	37: "MONITOR_TRAP_FLAG",
	39: "MONITOR_INSTRUCTION",
	40: "PAUSE_INSTRUCTION",
	41: "MCE_DURING_VMENTRY",
	43: "TPR_BELOW_THRESHOLD",
	44: "APIC_ACCESS",
	45: "EOI_INDUCED",
	46: "GDTR_IDTR",
	47: "LDTR_TR",
	48: "EPT_VIOLATION",
	49: "EPT_MISCONFIG",
	50: "INVEPT",
	51: "RDTSCP",
	52: "PREEMPTION_TIMER",
	53: "INVVPID",
	54: "WBINVD",
	55: "XSETBV",
	56: "APIC_WRITE",
	57: "RDRAND",
	58: "INVPCID",
	59: "VMFUNC",
	60: "ENCLS",
	61: "RDSEED",
	62: "PML_FULL",
	63: "XSAVES",
	64: "XRSTORS",
	67: "UMWAIT",
	68: "TPAUSE",
	74: "BUS_LOCK",
	75: "NOTIFY",
}

merged_states_aliases = {
	('0x30', '0x2040') : 'S1',
	('0x31', '0x2040') : 'S2',
	('0x31', '0x2060') : 'S3',
	('0x80050033', '0x2060') : 'S4',
	('0x80050033', '0x20f0') : 'S5',
	('0x80050033', '0x220f0') : 'S6',
	('0x80050033', '0x320f0') : 'S7',
	('0x80050033', '0x326f0') : 'S8',
	('0x80050033', '0x726f0') : 'S9',
}

def parse_line(line):
	content = line.split(']')[1].strip()
	fields = content.split(',')
	return fields

def process_to_dot(input_file_path, output_file_path, output_struct_path):
	valid_transitions = set()
	valid_transitions_kernel = set()
	transitions_occurences = defaultdict(int)
	
	with open(input_file_path, 'r') as input_file:
		lines = input_file.readlines()
		for index in range(len(lines) - 1):
			if index % 2 == 1:
				starting_fields = parse_line(lines[index - 1])
				starting_state = (starting_fields[2], starting_fields[3])
				starting_state_alias = merged_states_aliases[starting_state] 
				exit_reason = exit_reasons[int(starting_fields[5])]

				ending_fields = parse_line(lines[index])
				ending_state = (ending_fields[2], ending_fields[3])
				ending_state_alias = merged_states_aliases[ending_state]
				
				state_transition = (starting_state_alias, ending_state_alias, exit_reason)
				valid_transitions.add(state_transition)
				transitions_occurences[state_transition] += 1
				valid_transitions_kernel.add((int(starting_fields[2], 16), int(starting_fields[3], 16), int(starting_fields[5]), int(ending_fields[2], 16), int(ending_fields[3], 16), ))

	with open(output_file_path, 'w') as output_file:
		output_file.write("digraph FSM {\n    rankdir=LR;\n    node [shape=circle];\n    start [shape=box, width=0.2, label=""Start"", style=dashed];\n    start -> ""S1"";\n")
		for valid_transition in valid_transitions:
			output_file.write(f'    "{valid_transition[0]}" -> "{valid_transition[1]}" [label="{valid_transition[2]}"];\n')
		output_file.write("}")
	
	with open(output_struct_path, 'w') as struct_file:
		for valid_transition_kernel in valid_transitions_kernel:
			struct_file.write("{%d,%d,%d,%d,%d},\n" % (valid_transition_kernel[0], valid_transition_kernel[1], valid_transition_kernel[2], valid_transition_kernel[3], valid_transition_kernel[4]))
	
	with open("occurences_transitions.txt", 'w') as occurences:
		for (key, value) in transitions_occurences.items():
			occurences.write(f"{key[0]} & {key[1]} & {key[2]} & {value} \\ \n")

process_to_dot("oracle_trace_HEX.txt", "outputFSM.dot", "structFile.txt")