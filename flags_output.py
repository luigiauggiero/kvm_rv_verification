def process_lines(input_file, output_file):
    exit_reason_map = {
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

    cr4_bits = ["VME", "PVI", "TSD", "DE", "PSE", "PAE", "MCE", "PGE", "PCE", "OSFXSR", "OSXMMEXCPT", "UMIP", "LA57", "VMXE", "SMXE", "", "FSGSBASE", "PCIDE", "OSXSAVE", "", "SMEP", "SMAP", "PKE", "CET", "PKS", "UINTR", "", "", "LAM_SUP", "", "", ""]
    cr0_bits = ["PE", "MP", "EM", "TS", "ET", "NE", "", "", "", "", "", "", "", "", "", "", "WP", "", "AM", "", "", "", "", "", "", "", "", "", "", "NW", "CD", "PG"]
    efer_bits = ["SCE", "", "", "", "", "", "", "", "LME", "", "LMA", "NXE", "SVME", "LMSLE", "FFXSR", "TCE", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]

    def parse_line(line):
        content = line.split(']')[1].strip()
        fields = content.split(',')
        return fields

    def format_control_register(value_str, bits_list):
        if not value_str or value_str.strip() == '':
            return ""
            
        value = int(value_str, 16)
        binary = format(value, '032b')
        flags = []
        
        for i, bit in enumerate(binary):
            if bit == '1' and bits_list[31 - i]:
                flags.append(bits_list[31 - i])
                
        return '+'.join(flags) if flags else ""

    def format_EFER_register(value_str, bits_list):
        if not value_str or value_str.strip() == '':
            return ""
            
        value = int(value_str, 16)
        binary = format(value, '064b')
        flags = []
        
        for i, bit in enumerate(binary):
            if bit == '1' and bits_list[63 - i]:
                flags.append(bits_list[63 - i])
                
        return '+'.join(flags) if flags else ""

    with open(input_file, 'r') as f:
        lines = f.readlines()

    with open(output_file, 'w') as f:
        f.write("EXIT_NUMBER,VCPU_ID,CR0,CR4,EFER,EXIT_REASON\n")
        j = 0
        for line in lines:
            fields = parse_line(line)

            cr0 = format_control_register(fields[2], cr0_bits)
            cr4 = format_control_register(fields[3], cr4_bits)
            efer = format_EFER_register(fields[4], efer_bits)
            
            exit_reason = exit_reason_map[int(fields[5])]
            
            output_line = f"{fields[0]},{fields[1]},{cr0},{cr4},{efer},{exit_reason}\n"
            output_line = output_line.replace(",,", ",NULL,")
            output_line = output_line.replace(",\n", ",NULL\n")
            f.write(output_line)
            j += 1


input_file = 'oracle_trace_HEX.txt'
output_file = 'oracle_trace_FLAGS.txt'
process_lines(input_file, output_file)