import java.io.*;

public class zo
{
    private static class zavod_t
    {
        int idx; // offset 0x0
        byte[] name_boxed; // offset 0x8
        long name_len; // offset 0x10
        int num_workers; // offset 0x18
        int wtf; // offset 0x1c
        int build_year; // offset 0x20
        zavod_t next_boxed; // offset 0x28
    }
    private static int nz = 0;
    private static zavod_t z_head = null;
    private static boolean _in_have_buf = false;
    private static int _in_buf;
    private static boolean _success;
    private static int getchar() throws Exception
    {
        if(_in_have_buf)
        {
            _in_have_buf = false;
            return _in_buf;
        }
        return System.in.read();
    }
    private static long _read_num() throws Exception
    {
        long ans = 0;
        int c = getchar();
        _success = false;
        while(c == 32 || c == 9 || c == 10)
            c = getchar();
        while(c >= 48 && c < 58)
        {
            _success = true;
            ans = 10 * ans + c - 48;
            c = getchar();
        }
        _in_have_buf = true;
        _in_buf = c;
        return ans;
    }
    private static long read(InputStream fd, byte[] buf, long count) throws Exception
    {
        for(long i = 0; i < count; i++)
        {
            int c = getchar();
            if(c < 0)
                return i;
            buf[(int)i] = (byte)c;
        }
        return count;
    }
    private static void create_z() throws Exception
    {
        if(nz > 10)
            System.exit(1);
        System.out.print("name size: ");
        System.out.flush();
        long name_len = _read_num(); // -0x28(%rbp), 8 bytes
        getchar();
        if(name_len == 0 || name_len >= 0x7ff)
            System.exit(1);
        byte[] name_s = new byte[(int)(name_len + 1)]; // -0x20(%rbp)
        if(name_s == null)
            System.exit(1);
        System.out.print("enter name: ");
        System.out.flush();
        if(read(System.in, name_s, name_len) <= 0)
            System.exit(1);
        name_s[(int)name_len] = 0;
        zavod_t the_zavod = new zavod_t(); // -0x18(%rbp)
        if(the_zavod == null)
            System.exit(1);
        System.out.print("enter number of workers: ");
        System.out.flush();
        the_zavod.num_workers = (int)_read_num();
        getchar();
        System.out.print("is Zavod working (y/N): ");
        System.out.flush();
        int wtf = 0; // -0x10(%rbp), 4 bytes
        byte[] wtf_s = new byte[4];
        read(System.in, wtf_s, 4);
        for(int i = 3; i >= 0; i--)
            wtf = 256 * wtf + (((int)wtf_s[i])&255);
        System.out.print("enter year Zavod was built: ");
        System.out.flush();
        the_zavod.build_year = (int)_read_num();
        if(!_success)
            System.exit(1);
        getchar();
        the_zavod.wtf = 0;
        the_zavod.name_boxed = name_s;
        the_zavod.name_len = name_len;
        the_zavod.idx = nz++;
        System.out.print("Zavod number ");
        System.out.print(the_zavod.idx);
        System.out.println(" has been created\n");
        the_zavod.next_boxed = z_head;
        z_head = the_zavod;
    } 
    private static void edit_z() throws Exception
    {
        System.out.print("enter idx: ");
        System.out.flush();
        int idx = (int)_read_num(); // -0x24(%rbp)
        getchar();
        zavod_t the_zavod = z_head; // -0x20(%rbp)
        while(the_zavod != null && the_zavod.idx != idx)
            the_zavod = the_zavod.next_boxed;
        if(the_zavod == null || the_zavod.name_len == 0)
        {
            System.out.println("no such idx");
            return;
        }
        System.out.print("enter name: ");
        System.out.flush();
        byte[] name_s = the_zavod.name_boxed; // -0x18(%rbp)
        if(read(System.in, name_s, the_zavod.name_len) <= 0)
            System.exit(1);
        name_s[(int)the_zavod.name_len] = 0;
        System.out.print("enter number of workers: ");
        System.out.flush();
        the_zavod.num_workers = (int)_read_num();
        getchar();
        System.out.print("is z working (y/N): ");
        System.out.flush();
        int wtf = 0; // -0x10(%rbp)
        byte[] wtf_s = new byte[4];
        read(System.in, wtf_s, 4);
        for(int i = 3; i >= 0; i--)
            wtf = 256 * wtf + (((int)wtf_s[i])&255);
        the_zavod.wtf = 0;
        System.out.print("enter year Zavod was built: ");
        System.out.flush();
        the_zavod.build_year = (int)_read_num();
        if(!_success)
            System.exit(1);
        getchar();
    }
    private static void print_z() throws Exception
    {
        System.out.print("enter idx: ");
        System.out.flush();
        int idx = (int)_read_num(); // -0x14(%rbp)
        getchar();
        zavod_t the_zavod = z_head; // -0x10(%rbp)
        while(the_zavod != null && the_zavod.idx != idx)
            the_zavod = the_zavod.next_boxed;
        if(the_zavod == null || the_zavod.name_len == 0)
        {
            System.out.println("no such idx");
            return;
        }
        System.out.print("idx: ");
        System.out.println(the_zavod.idx);
        System.out.print("name: ");
        System.out.write(the_zavod.name_boxed, 0, (int)the_zavod.name_len);
        System.out.print("year built: ");
        System.out.println(the_zavod.build_year);
        System.out.print("is working: ");
        System.out.println((the_zavod.wtf!=0)?"Y":"N");
        System.out.print("number of workers: ");
        System.out.println(the_zavod.num_workers);
        System.out.println("=====================================================");
    }
    private static void delete_z() throws Exception
    {
        System.out.print("enter idx: ");
        System.out.flush();
        int idx = (int)_read_num(); // -0x14(%rbp)
        getchar();
        zavod_t the_zavod = z_head; // -0x10(%rbp)
        while(the_zavod != null && the_zavod.idx != idx)
            the_zavod = the_zavod.next_boxed;
        if(the_zavod == null)
            return;
        the_zavod.name_len = 0;
    }
    private static void print_welcome() throws Exception
    {
        System.out.println("+======================================+\n|Welcome to the ZAVOD storing platform!|\n| Here you can manage Zavods you have! |\n+======================================+");
    }
    private static void print_menu() throws Exception
    {
        System.out.println("1. Create Zavod");
        System.out.println("2. Edit Zavod");
        System.out.println("3. Delete Zavod");
        System.out.println("4. Print Zavod");
        System.out.println("5. Exit");
        System.out.print("> ");
        System.out.flush();
    }
    private static void init_stuff() throws Exception
    {
        FileInputStream fd = new FileInputStream("/dev/urandom"); // -0x4(%rbp)
        byte[] cookie = new byte[8];
        if(read(fd, cookie, 8) != 8)
            System.exit(1);
    }
    private static int main() throws Exception
    {
        print_welcome();
        for(;;)
        {
            print_menu();
            int cmd = (int)_read_num(); // -0xc(%rbp)
            if(!_success)
                return 0;
            getchar();
            switch(cmd)
            {
            case 1: create_z(); break;
            case 2: edit_z(); break;
            case 3: delete_z(); break;
            case 4: print_z(); break;
            default: System.exit(0);
            }
        }
    }
    public static void main(String[] argv)
    {
        try
        {
            System.exit(main());
        }
        catch(Exception e)
        {
            e.printStackTrace();
            System.exit(1);
        } 
    }
}
