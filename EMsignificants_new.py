import os

os.chdir('gwas')

#%%
def genotype_counts(line):        
    '''Ypologismos arithmou gonotupwn
    Input: grammi arxeiou se Genotype File Format 
    Output: tuple tis morfis (snp_ID, arithmos omozugwn atomwn gia to refrence allilomorfo, arithmos omozugwn atomwn gia to alternative allilomorfo, arithmos eterozugwn atomwn, sunolo atomwn, thesi SNP sumfwna me to NCBI build 36)'''
    
    splittedline= line.split(' ')   #einai lista, ta items tis anagnwrizontai ws strings
    snp= splittedline[0]
    N=(len(splittedline)-5)/3   #Arithmos atomwn. px ena line twn 500 atomwn: exei len=1505(3*N+5)
    locus=splittedline[2]
    
    homozygous_refrence=0 ;homozygous_alternative=0 ; heterozygous=0
    for i in range(5, len(splittedline) -len(splittedline)%3, 3): #!tsekare to range
        individual= splittedline[i] + splittedline[i+1] + splittedline[i+2]
        if individual=='100':
            homozygous_refrence+=1
        elif individual=='010':
            heterozygous+=1
        elif individual=='001':
            homozygous_alternative+=1
    return snp ,homozygous_refrence, homozygous_alternative, heterozygous, N, locus
            
#%%                
def allele_freq(x):   
    '''Ypologismos suxnotitas allilomorfwn (p=suxnotita refrence allilomorfou, q=suxnotita alternative allilomorfou)
    *Prepei prwta na treksi i genotype_counts*
    Input: tuple tis morfis (snp_ID, arithmos omozugwn atomwn gia to refrence allilomorfo, arithmos omozugwn atomwn gia to alternative allilomorfo, arithmos eterozugwn atomwn, sunolo atomwn, thesi SNP sumfwna me to NCBI build 36)
    Output: tuple (snp_ID, p, q) '''
    
    snp, R, A, het, N, loci = x
    p= round((R*2 + het)/(2*N), 3)  
    q= round((A*2 + het)/(2*N), 3)
    return snp, p, q
    
#%%  
def diplotupoi(snplist):
    '''Ypologismos twn diplotupwn pou xreiazontai gia na pragmatopoih8ei to haplotype estimation wste na upologistei to LD 2 thesewn
    Input: lista me 2 antikeimena: grammes twn 2 thesewn se Genotype File Format  
    Output: ???????????????????????'''    
    snpA, snpB=snplist    
    snpA_splitted=snpA.split(' ')        
    snpB_splitted=snpB.split(' ')
    RR=0 ; Rh=0 ; 
    hR=0 ; hh=0 ; 
     
    for i in range(5, len(snpA_splitted) -len(snpA_splitted)%3 ,3):
        #oi gonotupoi tou kathe atomou stis 2 theseis 
        a_individual= snpA_splitted[i] + snpA_splitted[i+1] + snpA_splitted[i+2]
        b_individual= snpB_splitted[i] + snpB_splitted[i+1] + snpB_splitted[i+2]
        
        #diplotupoi: to elegxw ana grammi
        if a_individual == '100':
            if b_individual == '100':
                RR+=1
            elif b_individual == '010':
                Rh+=1
        elif a_individual == '010':
            if b_individual == '100':
                hR+=1
            elif b_individual == '010':
                hh+=1
    return RR, Rh, hR, hh
#%%
def EM(pAB,pA, pB, diplotype): #diplotupe: einai tuple apo tin sunartisi
    EMrun=True
    count=0
    RR, Rh, hR, hh = diplotype
    
    while EMrun:
        count+=1
        E= 2*RR + Rh + hR + (pAB * (1 + pAB - pA - pB) * hh)/ (((pA - pAB) * (pB - pAB)) + pAB * (1 + pAB - pA - pB))
        
        pAB_new= E/1000    #kantw se sxesi me N   
        
        if abs(pAB_new - pAB)< 10**(-5):
            EMrun = False
        else:
            pAB=pAB_new
           
    return pAB_new #count 
#%%
with open('STUDY.association')as file:
    remove=[]
    
    for line in file:
        line=line.rstrip('\n')        
        splittedline= line.split(' ')
        
        if float(splittedline[2]) < 1e-06:           #des apo simeiwseis nefelis<3
            remove.append(splittedline[0])
#%%                 -------    O XAMOS   ------------
#import time            
with open('gwas.cases.gen') as file:
    counter=0 # metritis p vazei orio gia to mexri posa mh significant LD 8a koitaksoume
    saved=[] #lista gia ta significant LD
    snps=[] # lista me ta zeugh snp p 8a mpoun ston EM

    while counter < 1000:
        
        for line in file:
            line = line.rstrip('\n')
            splittedline=line.split(' ')
            snpA= 'snp_104100'#kanonika ta diavazei apo argsparse
            snpA_number= int(snpA.split('_')[1])
            snpB_number= snpA_number + 1
            snpB= 'snp_' + str(snpB_number)
            #print(splittedline[0])
            if splittedline[0]==snpA:
                snps.append(line)
            elif splittedline[0]==snpB:
                snps.append(line)
            elif len(snps)==2:
                break
                    
            #%%      YPOLOGISMOS pA pB
        if len(snps) == 2: # elegxoume oti exei gemisei h lista swsta 
            counts=list(map(genotype_counts, snps))
            alleles=list(map(allele_freq, counts))
            pA=alleles[0][1] ;pa=alleles[0][2]
            pb=alleles[1][2] ;pB=alleles[1][1]    
                    #%% 
            import random
            if pA==1 or pB==1 or pa==1 or pb==1: #grapse giati --> an ena allele einai egka8idrumeno ka8e allo pou 8a paei zeugri tou einai aneksarthto
                D=0 
            else:    
                diplotype= diplotupoi(snps)
                pABs=[random.uniform(0,1) for x in range(100)]
                    
            pAB_newS=[]
                
            for i in pABs:
                pAB_new= EM(i, pA, pB, diplotype)
                pAB_newS.append(pAB_new)
                            #print(pAB_new)    #edw i print
                        
                pAB_mean= sum(pAB_newS)/len(pAB_newS)  # apo ta pABnew p proekupsan ap tis 100 diaforetikes initial values vgazume ena meso oro gia thn timh pou 8a xrhsimopoihsoume  
                D= pAB_mean - (pA * pB)
                        
                    #%% 
                if D <0:
                    lista= [pA*pB, (1-pA) * (1-pB)]
                    Dmax= min(lista)
                        
                else:
                    lista=[pA*(1-pB), (1-pA)* pB]
                    Dmax= min(lista)
                              
                Dtonos= D/Dmax          
                    
                    
              #%%
                    
                if Dtonos > 0.25 : #
                    saved.append(snpB)
                    counter = 0
                    print(snpB_number, Dtonos) 
                    #snps=[]
                    #k+=1
           
                else:
                    counter += 1
                    #k+=1
                    print(snpB_number,"no significant LD")
                    
                snpB_number+=1
                snpB= 'snp_' + str(snpB_number)  
                snps=[]
          
        else:
            continue
                    
