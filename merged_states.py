from collections import defaultdict

cr0_aliases = {
	"0x80050033": "A1",
	"0x31": "A2",
	"0x30": "A3",
}

cr4_aliases = {
	"0x726f0": "B1",
	"0x326f0": "B2",
	"0x320f0": "B3",
	"0x220f0": "B4",
	"0x20f0": "B5",
	"0x2060": "B6",
	"0x2040": "B7",
}

def find_merged_states(input_file_path, output_file_path):
	merged_states = set()
	count_dictionary = defaultdict(int)

	with open(input_file_path, 'r') as input_file:
		lines = input_file.readlines()
		for line in lines:
			fields = line[15:].strip().split(",")
			cr0_value, cr4_value = fields[2].strip(), fields[3].strip()

			cr0_label = cr0_aliases.get(cr0_value, cr0_value)
			cr4_label = cr4_aliases.get(cr4_value, cr4_value)

			merged_state = (cr0_value, cr4_value)

			count_dictionary[merged_state] += 1

			merged_states.add(merged_state)

	with open(output_file_path, 'w') as output_file:
		for merged_state in merged_states:
			cr0_value, cr4_value = merged_state
			cr0_label = cr0_aliases.get(cr0_value, cr0_value)
			cr4_label = cr4_aliases.get(cr4_value, cr4_value)

			output_file.write(f"({cr0_label}_{cr4_label}) -> {count_dictionary[merged_state]} occurrences\n")

find_merged_states("oracle_trace_HEX.txt", "outputSTATES.txt")