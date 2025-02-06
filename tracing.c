#include <linux/module.h>
#include <linux/printk.h>
#include <linux/kvm.h>
#include <linux/kernel.h>
#include <linux/kprobes.h>
#include <linux/kvm_host.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Luigi Auggiero");
MODULE_DESCRIPTION("VMX_HANDLE_EXIT TRACING MODULE FOR x86 ARCHITECTURE");

/* Format string used for logging VM Exits in the module */ 
#define PRINT_FMT "%d,%d,0x%x,0x%x,0x%llx,%u\n"

/* VMCS fields HEX encoding, according to Intel Manual */
static uint64_t cr0_field = 0x6800;
static uint64_t cr4_field = 0x6804;
static uint64_t efer_field = 0x2806;
static uint64_t exit_field = 0x4402;

/* Integer variable to keep track of the number of exits */
static int exits_counter = 0;

/* Kprobe struct, as declared in Linux Kernel Documentation*/
static struct kprobe vmx_handle_exit_probe;

/* As Linux Kernel Documentation states, it needs to be explicitly declared even if not used */
static int vmx_handle_exit_pre_handler(struct kprobe *probe, struct pt_regs *regs)
{
    return 0;
}

/* Where the tracing logic is implemented */
static void vmx_handle_exit_post_handler(struct kprobe *probe, struct pt_regs *regs, unsigned long flags)
{
    uint64_t exit_value;
	uint64_t cr0_value;
    uint64_t cr4_value;
    uint64_t efer_value;
    
	exits_counter++;
	
    struct kvm_vcpu *vcpu = (struct kvm_vcpu *)regs->di;

    asm volatile("vmread %1, %0"
	            : "=r" (exit_value)
	            : "r" (exit_field)
	            : "cc");
   
    asm volatile("vmread %1, %0"
	    : "=r" (cr0_value)
	    : "r" (cr0_field)
	    : "cc");

    asm volatile("vmread %1, %0"
	    : "=r" (cr4_value)
	    : "r" (cr4_field)
	    : "cc");
	    
    asm volatile("vmread %1, %0"
	    : "=r" (efer_value)
	    : "r" (efer_field)
	    : "cc");
    
    printk(KERN_DEBUG PRINT_FMT, 
			exits_counter, vcpu->vcpu_id, (uint32_t)cr0_value, 
			(uint32_t)cr4_value, efer_value, (uint32_t)exit_value);
}

/* Module initializing function */
static int __init tracing_module_init(void)
{
    int register_result;
    
	vmx_handle_exit_probe.symbol_name = "vmx_handle_exit";
    vmx_handle_exit_probe.pre_handler = vmx_handle_exit_pre_handler;
    vmx_handle_exit_probe.post_handler = vmx_handle_exit_post_handler;
    
    register_result = register_kprobe(&vmx_handle_exit_probe);
    
    if (register_result < 0) {
        pr_err("VMX_HANDLE_EXIT probe attach failed!\n");
        return register_result;
    }
    
    pr_info("VMX_HANDLE_EXIT tracing module attached!\n");
    return 0;
};

/* Module cleanup function */
static void __exit tracing_module_exit(void) 
{
    unregister_kprobe(&vmx_handle_exit_probe);
    pr_info("VMX_HANDLE_EXIT tracing module detached!\n");
}

/* Module functions registration */
module_init(tracing_module_init);
module_exit(tracing_module_exit);
