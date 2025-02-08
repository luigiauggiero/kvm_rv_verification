#include <linux/kernel.h>
#include <linux/kprobes.h>
#include <linux/kvm.h>
#include <linux/kvm_host.h>
#include <linux/module.h>
#include <linux/printk.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Luigi Auggiero");
MODULE_DESCRIPTION(
	"CR0-INJECTION MODULE FOR FSM VALIDATION IN x86 ARCHITECTURE");

/* This macro sets a value for the KVM_VM_CR0_ALWAYS_OFF, defined as
the result of bitwise OR operation between X86_CR0_NW and X86_CR0_CD*/
#define KVM_VM_CR0_ALWAYS_OFF (X86_CR0_NW | X86_CR0_CD)

/* Kprobe struct, as declared in Linux Kernel Documentation*/
static struct kprobe vmx_handle_exit_probe;

/* VMCS fields HEX encoding, according to Intel Manual */
static uint64_t cr4_field = 0x6804;
static uint64_t cr0_field = 0x6800;
static uint64_t cr0_shadow_field = 0x6004;
static uint64_t exit_field = 0x4402;
static uint64_t efer_field = 0x2806;

/* Integer variable to keep track of the number of exits */
static int exits_counter = 0;

static int vmx_handle_exit_pre_handler(struct kprobe *probe,
									   struct pt_regs *regs) {
	exits_counter++;

	/* The 100th VM Exit is designated as the injection receiver */
	if (exits_counter == 100) {
		uint64_t cr0_value;
		uint64_t hw_cr0_value;

		/* A late-stage CR0 state is injected during early OS boot*/
		cr0_value = 0x80050033;

		/* According to the KVM source code, CR0 is modified as follows */
		hw_cr0_value = (cr0_value & ~KVM_VM_CR0_ALWAYS_OFF);

		/* According to the KVM source code, CR0 shadow is modified as follows
		 */
		asm volatile("vmwrite %1, %0"
					 : "=r"(cr0_shadow_field)
					 : "r"(cr0_value)
					 : "cc");

		asm volatile("vmwrite %1, %0"
					 : "=r"(cr0_field)
					 : "r"(hw_cr0_value)
					 : "cc");

		/* KVM vCPU struct */
		struct kvm_vcpu *vcpu = (struct kvm_vcpu *)regs->di;

		/* According to the KVM source code, KVM CRO is modified as follows */
		vcpu->arch.cr0 = cr0_value;
		printk(KERN_DEBUG "Injected 0x80050033 value in CR0!\n");
	}

	return 0;
}

static int __init tracing_module_init(void) {
	int register_result;

	vmx_handle_exit_probe.pre_handler = vmx_handle_exit_pre_handler;
	vmx_handle_exit_probe.symbol_name = "vmx_handle_exit";

	register_result = register_kprobe(&vmx_handle_exit_probe);
	if (register_result < 0) {
		pr_err("VMX_HANDLE_EXIT probe attach failed!\n");
		return register_result;
	}
	pr_info("Injection module attached!\n");
	return 0;
};

static void __exit tracing_module_exit(void) {
	unregister_kprobe(&vmx_handle_exit_probe);
	pr_info("Injection module detached!\n");
}

module_init(tracing_module_init);
module_exit(tracing_module_exit);
