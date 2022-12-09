Search.setIndex({docnames:["changelog","index","source/cloud_select","source/cloud_select.client","source/cloud_select.main","source/cloud_select.main.cloud","source/cloud_select.main.cloud.aws","source/cloud_select.main.cloud.google","source/cloud_select.main.solve","source/cloud_select.utils","source/modules"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":3,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":2,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,"sphinx.ext.todo":2,"sphinx.ext.viewcode":1,sphinx:56},filenames:["changelog.md","index.rst","source/cloud_select.rst","source/cloud_select.client.rst","source/cloud_select.main.rst","source/cloud_select.main.cloud.rst","source/cloud_select.main.cloud.aws.rst","source/cloud_select.main.cloud.google.rst","source/cloud_select.main.solve.rst","source/cloud_select.utils.rst","source/modules.rst"],objects:{"":{cloud_select:[2,0,0,"-"]},"cloud_select.client":{add_instance_arguments:[3,1,1,""],config:[3,0,0,"-"],get_parser:[3,1,1,""],instance:[3,0,0,"-"],run:[3,1,1,""],shell:[3,0,0,"-"]},"cloud_select.client.config":{main:[3,1,1,""]},"cloud_select.client.instance":{main:[3,1,1,""]},"cloud_select.client.shell":{bpython:[3,1,1,""],create_client:[3,1,1,""],ipython:[3,1,1,""],main:[3,1,1,""],python:[3,1,1,""]},"cloud_select.logger":{ColorizingStreamHandler:[2,2,1,""],LogColors:[2,2,1,""],Logger:[2,2,1,""],add_prefix:[2,1,1,""],setup_logger:[2,1,1,""],underline:[2,1,1,""]},"cloud_select.logger.ColorizingStreamHandler":{BLACK:[2,3,1,""],BLUE:[2,3,1,""],BOLD_SEQ:[2,3,1,""],COLOR_SEQ:[2,3,1,""],CYAN:[2,3,1,""],GREEN:[2,3,1,""],MAGENTA:[2,3,1,""],RED:[2,3,1,""],RESET_SEQ:[2,3,1,""],WHITE:[2,3,1,""],YELLOW:[2,3,1,""],can_color_tty:[2,4,1,""],colors:[2,3,1,""],decorate:[2,4,1,""],emit:[2,4,1,""],is_tty:[2,4,1,""]},"cloud_select.logger.LogColors":{BOLD:[2,3,1,""],ENDC:[2,3,1,""],OKBLUE:[2,3,1,""],OKCYAN:[2,3,1,""],OKGREEN:[2,3,1,""],PURPLE:[2,3,1,""],RED:[2,3,1,""],UNDERLINE:[2,3,1,""],WARNING:[2,3,1,""]},"cloud_select.logger.Logger":{cleanup:[2,4,1,""],debug:[2,4,1,""],error:[2,4,1,""],exit:[2,4,1,""],handler:[2,4,1,""],info:[2,4,1,""],location:[2,4,1,""],progress:[2,4,1,""],set_level:[2,4,1,""],set_stream_handler:[2,4,1,""],shellcmd:[2,4,1,""],text_handler:[2,4,1,""],warning:[2,4,1,""],yellow:[2,4,1,""]},"cloud_select.main":{cache:[4,0,0,"-"],client:[4,0,0,"-"],cloud:[5,0,0,"-"],colors:[4,0,0,"-"],schemas:[4,0,0,"-"],settings:[4,0,0,"-"],solve:[8,0,0,"-"],table:[4,0,0,"-"]},"cloud_select.main.cache":{Cache:[4,2,1,""]},"cloud_select.main.cache.Cache":{clear:[4,4,1,""],exists:[4,4,1,""],get:[4,4,1,""],get_cache_name:[4,4,1,""],is_expired:[4,4,1,""],set:[4,4,1,""]},"cloud_select.main.client":{Client:[4,2,1,""]},"cloud_select.main.client.Client":{get_clouds:[4,4,1,""],instance_select:[4,4,1,""],instances:[4,4,1,""],load_cache:[4,4,1,""],prices:[4,4,1,""],set_clouds:[4,4,1,""],update_from_cache:[4,4,1,""]},"cloud_select.main.cloud":{aws:[6,0,0,"-"],base:[5,0,0,"-"],google:[7,0,0,"-"]},"cloud_select.main.cloud.aws":{client:[6,0,0,"-"],instance:[6,0,0,"-"],prices:[6,0,0,"-"]},"cloud_select.main.cloud.aws.client":{AmazonCloud:[6,2,1,""]},"cloud_select.main.cloud.aws.client.AmazonCloud":{instances:[6,4,1,""],load_instances:[6,4,1,""],load_prices:[6,4,1,""],name:[6,3,1,""],prices:[6,4,1,""]},"cloud_select.main.cloud.aws.instance":{AmazonInstance:[6,2,1,""],AmazonInstanceGroup:[6,2,1,""]},"cloud_select.main.cloud.aws.instance.AmazonInstance":{attr_cpus:[6,4,1,""],attr_description:[6,4,1,""],attr_free_tier:[6,4,1,""],attr_gpu:[6,4,1,""],attr_gpus:[6,4,1,""],attr_ipv6:[6,4,1,""],attr_memory:[6,4,1,""],attr_price:[6,4,1,""],attr_region:[6,4,1,""],name:[6,4,1,""]},"cloud_select.main.cloud.aws.instance.AmazonInstanceGroup":{Instance:[6,3,1,""],add_instance_prices:[6,4,1,""],filter_region:[6,4,1,""],iter_instances:[6,4,1,""],name_attribute:[6,3,1,""]},"cloud_select.main.cloud.aws.prices":{AmazonPrices:[6,2,1,""]},"cloud_select.main.cloud.base":{CloudData:[5,2,1,""],CloudDataEncoder:[5,2,1,""],CloudProvider:[5,2,1,""],Instance:[5,2,1,""],InstanceGroup:[5,2,1,""],Prices:[5,2,1,""]},"cloud_select.main.cloud.base.CloudData":{Encoder:[5,3,1,""],create_lookup:[5,4,1,""]},"cloud_select.main.cloud.base.CloudDataEncoder":{"default":[5,4,1,""]},"cloud_select.main.cloud.base.CloudProvider":{fail_message:[5,4,1,""],instances:[5,4,1,""],load_instances:[5,4,1,""],name:[5,3,1,""]},"cloud_select.main.cloud.base.Instance":{attr_description:[5,4,1,""],attr_zone:[5,4,1,""],attribute_getters:[5,4,1,""],cloud:[5,4,1,""],generate_row:[5,4,1,""],name:[5,4,1,""]},"cloud_select.main.cloud.base.InstanceGroup":{Instance:[5,3,1,""],add_instance_prices:[5,4,1,""],filter_region:[5,4,1,""],generate_row:[5,4,1,""],iter_instances:[5,4,1,""]},"cloud_select.main.cloud.google":{client:[7,0,0,"-"],instance:[7,0,0,"-"],prices:[7,0,0,"-"]},"cloud_select.main.cloud.google.client":{GoogleCloud:[7,2,1,""]},"cloud_select.main.cloud.google.client.GoogleCloud":{instances:[7,4,1,""],load_instances:[7,4,1,""],load_prices:[7,4,1,""],name:[7,3,1,""],prices:[7,4,1,""]},"cloud_select.main.cloud.google.instance":{GoogleCloudInstance:[7,2,1,""],GoogleCloudInstanceGroup:[7,2,1,""]},"cloud_select.main.cloud.google.instance.GoogleCloudInstance":{attr_cpus:[7,4,1,""],attr_free_tier:[7,4,1,""],attr_gpu:[7,4,1,""],attr_gpus:[7,4,1,""],attr_ipv6:[7,4,1,""],attr_memory:[7,4,1,""],attr_price:[7,4,1,""],attr_region:[7,4,1,""]},"cloud_select.main.cloud.google.instance.GoogleCloudInstanceGroup":{Instance:[7,3,1,""],add_instance_prices:[7,4,1,""],filter_region:[7,4,1,""],name_attribute:[7,3,1,""]},"cloud_select.main.cloud.google.prices":{GoogleCloudPrices:[7,2,1,""]},"cloud_select.main.colors":{get_random_color:[4,1,1,""],get_rich_color:[4,1,1,""],get_rich_colors:[4,1,1,""]},"cloud_select.main.settings":{OrderedList:[4,1,1,""],Settings:[4,2,1,""]},"cloud_select.main.settings.Settings":{"delete":[4,4,1,""],add:[4,4,1,""],change_validate:[4,4,1,""],edit:[4,4,1,""],ensure_filesystem_registry:[4,4,1,""],filesystem_registry:[4,4,1,""],get:[4,4,1,""],get_settings_file:[4,4,1,""],inituser:[4,4,1,""],load:[4,4,1,""],parse_boolean:[4,4,1,""],parse_null:[4,4,1,""],remove:[4,4,1,""],save:[4,4,1,""],set:[4,4,1,""],update_param:[4,4,1,""],update_params:[4,4,1,""],validate:[4,4,1,""]},"cloud_select.main.solve":{database:[8,0,0,"-"],properties:[8,0,0,"-"],solver:[8,0,0,"-"]},"cloud_select.main.solve.database":{Database:[8,2,1,""],parse_range:[8,1,1,""],parse_value:[8,1,1,""],with_connection:[8,2,1,""]},"cloud_select.main.solve.database.Database":{add_instance:[8,4,1,""],execute:[8,4,1,""],execute_many:[8,4,1,""],filter_instances:[8,4,1,""]},"cloud_select.main.solve.properties":{Properties:[8,2,1,""]},"cloud_select.main.solve.properties.Properties":{not_solver_properties:[8,3,1,""],range_properties:[8,3,1,""],set_gpu_properties:[8,4,1,""],set_not_solver_properties:[8,4,1,""],set_properties:[8,4,1,""],set_range_properties:[8,4,1,""],skip_patterns:[8,3,1,""]},"cloud_select.main.solve.solver":{Solver:[8,2,1,""]},"cloud_select.main.solve.solver.Solver":{add_instances:[8,4,1,""],add_properties:[8,4,1,""],solve:[8,4,1,""]},"cloud_select.main.table":{Table:[4,2,1,""]},"cloud_select.main.table.Table":{available_width:[4,4,1,""],ensure_complete:[4,4,1,""],ensure_complete_list:[4,4,1,""],table:[4,4,1,""],table_columns:[4,4,1,""],table_rows:[4,4,1,""]},"cloud_select.utils":{fileio:[9,0,0,"-"],misc:[9,0,0,"-"],terminal:[9,0,0,"-"]},"cloud_select.utils.fileio":{can_be_deleted:[9,1,1,""],copyfile:[9,1,1,""],creation_date:[9,1,1,""],get_file_hash:[9,1,1,""],get_tmpdir:[9,1,1,""],get_tmpfile:[9,1,1,""],mkdir_p:[9,1,1,""],mkdirp:[9,1,1,""],print_json:[9,1,1,""],read_file:[9,1,1,""],read_json:[9,1,1,""],read_yaml:[9,1,1,""],recursive_find:[9,1,1,""],remove_to_base:[9,1,1,""],write_file:[9,1,1,""],write_json:[9,1,1,""],write_yaml:[9,1,1,""]},"cloud_select.utils.misc":{chunks:[9,1,1,""]},"cloud_select.utils.terminal":{check_install:[9,1,1,""],confirm_action:[9,1,1,""],confirm_uninstall:[9,1,1,""],ensure_no_extra:[9,1,1,""],get_installdir:[9,1,1,""],run_command:[9,1,1,""],which:[9,1,1,""]},cloud_select:{client:[3,0,0,"-"],defaults:[2,0,0,"-"],logger:[2,0,0,"-"],main:[4,0,0,"-"],utils:[9,0,0,"-"],version:[2,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","function","Python function"],"2":["py","class","Python class"],"3":["py","attribute","Python attribute"],"4":["py","method","Python method"]},objtypes:{"0":"py:module","1":"py:function","2":"py:class","3":"py:attribute","4":"py:method"},terms:{"128":4,"208":6,"91m":2,"92m":2,"93m":2,"94m":2,"95m":2,"96m":2,"abstract":5,"boolean":4,"case":9,"char":2,"class":[2,4,5,6,7,8],"default":[1,4,5,9,10],"final":8,"float":8,"function":[4,5,8],"long":9,"new":4,"null":4,"return":[2,4,5,6,7,8,9],"true":[4,5,8,9],"try":5,And:7,For:[5,7],The:[2,6,7,9],There:8,These:8,Use:[6,7,8],_could_:7,_io:2,a100:7,abil:8,acceler:7,access:6,action:[4,9],add:[2,4,5,6,7,8],add_inst:8,add_instance_argu:3,add_instance_pric:[5,6,7],add_prefix:2,add_properti:8,added:[7,8],addit:4,address:7,akin:9,alert:9,algorithm:9,alia:[5,6,7],all:[5,7,9],allow:[4,5,6,7],allow_nan:5,also:[5,9],alwai:5,amazon:6,amazonaw:6,amazoncloud:6,amazoninst:6,amazoninstancegroup:6,amazonpric:6,ani:[4,5],anoth:9,anyth:4,api:[6,7],append:2,applic:9,appropri:4,arbitrari:5,arg:3,argument:[8,9],argumnt:8,ascend:4,ask:9,assum:8,attempt:[4,9],attr_cpu:[6,7],attr_descript:[5,6],attr_free_ti:[6,7],attr_gpu:[6,7],attr_ipv6:[6,7],attr_memori:[6,7],attr_pric:[6,7],attr_region:[6,7],attr_zon:5,attribut:[2,3,5,6,8],attribute_gett:5,auth:5,authent:[4,7],avail:[4,7],available_width:4,aws:[4,5],base:[2,4,6,7,8,9],base_path:9,best:7,black:2,blue:2,bold:2,bold_seq:2,both:8,boto3:6,bpython:3,cach:[2,5,6,7,10],cache_dir:4,cache_expir:4,calcul:4,call:5,can:[4,5,6,7,9],can_be_delet:9,can_color_tti:2,cannot:[4,6,7],categori:7,certain:9,chang:[4,7],change_valid:4,changelog:0,check:[4,9],check_circular:5,check_instal:9,chunk:9,chunk_siz:9,chunkifi:9,clean:8,cleanup:2,clear:4,client:[1,2,5,10],clingo:8,close:8,cloud:[2,4,8,9],cloud_nam:[4,8],cloud_select:1,clouddata:5,clouddataencod:5,cloudprovid:[5,6,7],cls:[4,9],cmd:9,color:[2,10],color_seq:2,colorizingstreamhandl:2,column:4,com:[6,7],come:8,command:[3,4,8,9],comment:9,commit1mo:7,commit1yr:7,commit3yr:7,common:5,comput:[6,7],config:[2,4,10],configur:[4,7],confirm:[4,9],confirm_act:9,confirm_uninstal:9,conn:8,connect:8,consist:4,consol:2,consolid:8,contain:9,content:[1,10],copi:9,copyfil:9,could:[5,7],courtesi:4,cpu:[6,7,8],creat:[4,8,9],create_cli:3,create_lookup:5,creation:9,creation_d:9,criteria:9,critic:2,current:6,custom:4,cyan:2,data:[4,5,6,7],databas:[2,4],datatyp:4,date:9,debug:2,decor:[2,8],def:5,defin:[5,8],delet:[4,9],deriv:[3,5],descript:6,desir:8,destin:9,determin:[2,4,6,7],dict:5,dictionari:9,differ:5,directori:9,dirnam:9,doc:7,document:6,doe:[4,7,9],doesn:8,doing:4,done:2,down:[6,7,8],each:[4,5],edit:4,effort:7,either:8,els:5,emit:2,empti:[5,9],enabl:[4,6],encod:[2,4,5],end:8,endc:2,endpoint:4,engin:[6,7],ensur:[4,9],ensure_ascii:5,ensure_complet:4,ensure_complete_list:4,ensure_filesystem_registri:4,ensure_no_extra:9,entri:[4,9],entrypoint:3,error:[2,9],error_messag:9,estim:7,exampl:5,except:[2,5],exclude_list:8,exec:9,execut:[8,9],execute_mani:8,exist:[4,9],exit:2,expans:4,expect:4,expir:4,expos:5,express:[6,7],extra:[3,6,9],fail:9,fail_messag:5,fallback:9,fals:[2,4,5,8,9],far:7,featur:7,field:4,file:[4,9],fileio:[2,10],filenam:[4,8,9],filesystem:4,filesystem_registri:4,filter:[5,6,7,8],filter_inst:8,filter_region:[5,6,7],find:9,first:4,flag:8,flat:8,fly:4,forc:[4,9],format:[2,4],formatt:2,found:4,free:[6,7],from:[4,5,6,7,8,9],func:8,gener:[3,4,8],generate_row:5,get:[4,5,8,9],get_cache_nam:4,get_cloud:4,get_file_hash:9,get_instal:9,get_installdir:9,get_pars:3,get_random_color:4,get_rich_color:4,get_settings_fil:4,get_tmpdir:9,get_tmpfil:9,give:9,given:[4,5,7,8],googl:[4,5,6],googlecloud:7,googlecloudinst:7,googlecloudinstancegroup:7,googlecloudpric:7,gpu:[6,7,8],gpu_memori:8,green:2,group:[5,6,7],handl:[6,7],handler:2,has:[2,4,6,7],hash:9,have:[4,5,7,8],here:[6,8],home:4,hour:[6,7,8],how:[2,5],hpc:3,html:6,http:[6,7],ignore_fil:9,image_path:9,implement:5,includ:4,include_list:8,indent:5,index:1,info:2,inform:[2,5,6,7],init:7,initus:4,instal:[6,7,9],instanc:[2,4,5,8,10],instance_group:8,instance_select:4,instance_storag:8,instancegroup:[5,6,7],instancetyp:6,instanti:[5,8],instead:8,integ:4,interact:[4,5,6,7,8],ipv6:[6,7],ipython:3,is_expir:4,is_tti:2,isn:7,item:[4,5,6,7],iter:5,iter_inst:[5,6],its:[5,9],join:7,json:[4,5,6,7,9],json_obj:9,jsonencod:5,jsonschema:4,just:[4,6,8],kei:[4,8],know:5,known:[4,8],kwarg:[4,6,7,8],later:[5,8],latest:6,let:5,level:[2,9],licens:7,like:[5,6],limit:4,line:[4,8,9],linux:6,list:[4,5,7,9],littl:6,load:[4,5,6,7,9],load_cach:4,load_inst:[5,6,7],load_pric:[6,7],locat:2,log:2,logcolor:2,logger:[1,10],look:6,lookup:[4,5],machin:7,magenta:2,main:[1,2,3,10],make:[5,6,9],manual:8,match:[4,9],max:8,max_result:4,memori:[6,7,8],messag:[2,5,9],method:5,might:8,min:8,misc:[2,10],miss:4,mkdir:9,mkdir_p:9,mkdirp:9,mode:[2,9],modifi:9,modul:[1,10],monthli:7,more:9,msg:2,must:7,name:[2,4,5,6,7,8],name_attribut:[6,7],necessarili:7,nest:4,network:7,newlin:2,nocolor:2,none:[2,4,5,8,9],not_solver_properti:8,now:7,number:[6,7,8],nvidia:7,obj:9,object:[2,4,5,8],okblu:2,okcyan:2,okgreen:2,ondemand:[6,7],one:[6,8,9],onli:[4,6,9],open:8,oper:9,optim:7,option:9,orchestr:8,order:4,orderedlist:4,origin:8,other:[4,5,6,7],otherwis:4,our:5,output:2,over:[5,6,7],overrid:5,packag:[1,10],param:4,paramet:[4,9],parent:9,pars:[4,8],parse_boolean:4,parse_nul:4,parse_rang:8,parse_valu:8,parser:3,particular:9,pass:5,path:[5,9],pattern:9,per:[6,7,8],perform:9,popul:6,possibl:7,preambl:7,preemptibl:7,prefer:4,prefix:[2,9],present:[2,6],preserv:[4,9],pretti:[4,9],price:[4,5,8],print:[2,4,9],print_except:2,print_json:9,printshellcmd:2,proce:7,progress:2,prompt:9,prop:8,properti:[2,4,5,6],provid:[4,5,6,7,8],purpl:2,put:6,python:[3,8],queri:[5,6,7,8],question:9,quiet:[2,9],rais:5,ram:6,random:4,randomli:4,rang:8,range_gpu:8,range_properti:8,raw:[5,6,7],read:9,read_fil:9,read_json:9,read_yaml:9,record:2,recursive_find:9,red:2,refactor:8,refer:6,region:[5,6,7],registri:4,regular:[6,7],remov:[4,9],remove_to_bas:9,request:[3,6,7,8],requir:5,reset:8,reset_seq:2,resourc:1,result:[4,5],retriev:[4,5,6,7],return_cod:2,rich:4,roundtrip:9,row:[4,5],rule:8,run:[3,7,9],run_cloud_select:3,run_command:9,sai:7,save:[4,9],schema:[2,8,10],select:[4,8,9],self:[5,8],send:9,separ:5,serializ:5,serv:7,servic:6,set:[2,5,6,7,8,10],set_cloud:4,set_gpu_properti:8,set_level:2,set_not_solver_properti:8,set_properti:8,set_range_properti:8,set_stream_handl:2,settings_fil:4,setup:8,setup_logg:2,sha256:9,share:[4,5],shell:[2,10],shellcmd:2,should:[5,9],sinc:8,singl:[5,6,8],singular:[3,9],skip:9,skip_pattern:8,skipkei:5,softwar:9,solv:[2,4],solver:[2,4,6,7],somewher:7,sort_bi:4,sort_kei:5,sourc:[2,3,4,5,6,7,8,9],specif:[4,6,7,8],specifi:[2,9],start:4,state:8,stderr:2,stdout:2,storag:7,store:[5,6,7],stream:[2,9],stream_handl:2,streamhandl:2,string:8,strip_newlin:9,subclass:5,submodul:[1,10],subnet:7,subpackag:[1,10],subpars:3,subprocess:9,substitut:4,success:9,sudo:9,support:[5,6,7,8],tabl:[2,10],table_column:4,table_row:4,tell:7,temporari:9,termin:[2,10],text_handl:2,textiowrapp:2,thei:[4,7,9],them:9,thi:[4,5,6,7,8,9],thing:4,tier:[6,7],titl:4,tmpdir:9,togeth:6,tool:1,total:2,traceback:2,tradit:4,trail:2,tree:9,truncat:4,type:[4,5,7],typeerror:5,typic:4,typo:9,under:9,underlin:2,uninstal:9,unknown:8,unlik:4,updat:4,update_from_cach:4,update_param:4,url:4,usag:7,usd:[6,7],use:[7,9],use_thread:2,used:[2,7,8],user:[4,9],uses:[8,9],using:2,utf:2,util:[1,2,10],valid:4,valu:[4,8],vcpu:6,version:[1,9,10],want:[5,7,9],warn:2,when:[4,8],where:9,which:9,white:2,width:4,with_connect:8,within:[6,7],without:9,wms_monitor:2,work:6,wrap:[4,7],wrapper:[6,7],write:9,write_fil:9,write_json:9,write_yaml:9,written:2,x1b:2,yaml:[4,9],yellow:2,yet:7,yield:[4,6,9],yike:8,you:[5,7],your:7},titles:["&lt;no title&gt;","Welcome to Cloud Select\u2019s documentation!","cloud_select package","cloud_select.client package","cloud_select.main package","cloud_select.main.cloud package","cloud_select.main.cloud.aws package","cloud_select.main.cloud.google package","cloud_select.main.solve package","cloud_select.utils package","cloud_select"],titleterms:{"default":2,aws:6,base:5,cach:4,client:[3,4,6,7],cloud:[1,5,6,7],cloud_select:[2,3,4,5,6,7,8,9,10],color:4,config:3,content:[2,3,4,5,6,7,8,9],databas:8,document:1,fileio:9,googl:7,indic:1,instanc:[3,6,7],logger:2,main:[4,5,6,7,8],misc:9,modul:[2,3,4,5,6,7,8,9],packag:[2,3,4,5,6,7,8,9],price:[6,7],properti:8,schema:4,select:1,set:4,shell:3,solv:8,solver:8,submodul:[2,3,4,5,6,7,8,9],subpackag:[2,4,5],tabl:[1,4],termin:9,util:9,version:2,welcom:1}})
