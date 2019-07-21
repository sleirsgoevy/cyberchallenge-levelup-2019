#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>

typedef struct
{
    int idx; // offset 0x0
    char padding[0x4];
    intptr_t name_boxed; // offset 0x8
    size_t name_len; // offset 0x10
    int num_workers; // offset 0x18
    int wtf; // offset 0x1c
    int build_year; // offset 0x20
    char padding2[0x4];
    intptr_t next_boxed; // offset 0x28
} __attribute__((packed)) zavod_t;


intptr_t cookie;
int nz;
zavod_t* z_head;

void create_z()
{
    if(nz > 10)
        exit(1);
    printf("name size: ");
    size_t name_len; // -0x28(%rbp), 8 bytes
    if(scanf("%zu", &name_len) != 1)
        exit(1);
    getchar();
    if(name_len == 0 || name_len >= 0x7ff)
        exit(1);
    char* name_s = malloc(name_len + 1); // -0x20(%rbp)
    if(name_s == 0)
        exit(1);
    printf("enter name: ");
    if(read(0, name_s, name_len) <= 0)
        exit(1);
    name_s[name_len] = 0;
    zavod_t* the_zavod = malloc(0x30); // -0x18(%rbp)
    if(the_zavod == 0)
        exit(1);
    printf("enter number of workers: ");
    scanf("%d", &the_zavod->num_workers);
    getchar();
    printf("is Zavod working (y/N): ");
    int wtf; // -0x10(%rbp), 4 bytes
    read(0, &wtf, 4);
    printf("enter year Zavod was built: ");
    if(scanf("%d", &the_zavod->build_year) != 1)
        exit(1);
    getchar();
    the_zavod->wtf = 0;
    the_zavod->name_boxed = ((intptr_t)name_s) ^ cookie;
    the_zavod->name_len = name_len;
    the_zavod->idx = nz++;
    printf("Zavod number %d has been created\n", the_zavod->idx);
    the_zavod->next_boxed = ((intptr_t)the_zavod)^((intptr_t)z_head)^cookie;
    z_head = the_zavod;
}

void edit_z()
{
    printf("enter idx: ");
    int idx; // -0x24(%rbp)
    scanf("%d", &idx);
    getchar();
    zavod_t* the_zavod = z_head; // -0x20(%rbp)
    while(the_zavod && the_zavod->idx != idx)
        the_zavod = (zavod_t*)(the_zavod->next_boxed^((intptr_t)the_zavod)^cookie);
    if(!the_zavod || the_zavod->name_len == 0)
    {
        puts("no such idx");
        return;
    }
    printf("enter name: ");
    char* name_s = (char*)(the_zavod->name_boxed^cookie); // -0x18(%rbp)
    if(read(0, name_s, the_zavod->name_len) <= 0)
        exit(1);
    name_s[the_zavod->name_len] = 0;
    printf("enter number of workers: ");
    scanf("%d", &the_zavod->num_workers);
    getchar();
    printf("is z working (y/N): ");
    int wtf; // -0x10(%rbp)
    read(0, &wtf, 4);
    the_zavod->wtf = 0;
    printf("enter year Zavod was built: ");
    if(scanf("%d", &the_zavod->build_year) != 1)
        exit(1);
    getchar();
}

void print_z()
{
    printf("enter idx: ");
    int idx; // -0x14(%rbp)
    scanf("%d", &idx);
    getchar();
    zavod_t* the_zavod = z_head; // -0x10(%rbp)
    while(the_zavod && the_zavod->idx != idx)
        the_zavod = (zavod_t*)(the_zavod->next_boxed^((intptr_t)the_zavod)^cookie);
    if(!the_zavod || the_zavod->name_len == 0)
    {
        puts("no such idx");
        return;
    }
    printf("idx: %d\n", the_zavod->idx);
    printf("name: ");
    write(1, (char*)(the_zavod->name_boxed^cookie), the_zavod->name_len);
    printf("year built: %d\n", the_zavod->build_year);
    printf("is working: %s\n", (the_zavod->wtf)?"Y":"N");
    printf("number of workers: %d\n", the_zavod->num_workers);
    puts("=====================================================");
}

void delete_z()
{
    printf("enter idx: ");
    int idx; // -0x14(%rbp)
    scanf("%d", &idx);
    getchar();
    zavod_t* the_zavod = z_head; // -0x10(%rbp)
    while(the_zavod && the_zavod->idx != idx)
        the_zavod = (zavod_t*)(the_zavod->next_boxed^((intptr_t)the_zavod)^cookie);
    if(the_zavod == 0)
        return;
    free((void*)(the_zavod->name_boxed^cookie));
    the_zavod->name_len = 0;
}

void print_welcome()
{
    puts("+======================================+\n|Welcome to the ZAVOD storing platform!|\n| Here you can manage Zavods you have! |\n+======================================+");
}

void print_menu()
{
    puts("1. Create Zavod");
    puts("2. Edit Zavod");
    puts("3. Delete Zavod");
    puts("4. Print Zavod");
    puts("5. Exit");
    printf("> ");
}

void init_stuff()
{
    int fd = open("/dev/urandom", 0); // -0x4(%rbp)
    if(fd < 0)
        exit(1);
    if(read(fd, &cookie, 8) != 8)
        exit(1);
    close(fd);
}

int main()
{
    setvbuf(stdin, 0, 2, 0);
    setvbuf(stdout, 0, 2, 0);
    alarm(0x1e);
    print_welcome();
    for(;;)
    {
        print_menu();
        int cmd; // -0xc(%rbp)
        if(scanf("%d", &cmd) != 1)
            exit(0);
        getchar();
        switch(cmd)
        {
        case 1: create_z(); break;
        case 2: edit_z(); break;
        case 3: delete_z(); break;
        case 4: print_z(); break;
        default: exit(0);
        }
    }
}
