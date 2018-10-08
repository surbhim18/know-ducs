import boto3

s3 = boto3.client('s3')
client = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')

#no update trigger yet
def csv_reader(event,context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    obj = s3.get_object(Bucket=bucket,Key=key)
    
    rows = obj['Body'].read().decode("utf-8").split('\n')
    rows = rows[:-1]
    print(rows)
    
    #access first four rows directly
    faculty = rows[0].split(',')[1]
    print(faculty)
    department = rows[1].split(',')[1]
    print(department)
    code = rows[2].split(',')[1]
    year = rows[3].split(',')[1]
    print(year)
    #ignore two rows

    rowx = rows[6:] 
    print(rowx)
   
    #creating table dynamically
    table_name = "Admission_"+year
    response = client.list_tables()

    #check if table already exists
    if table_name in response['TableNames']:
        table_found = True
    else:
        table_found = False
        
    if table_found == False:
        table = dynamodb.create_table(
            TableName = table_name,
            KeySchema =[
                { 'AttributeName': "programme", 'KeyType': "HASH" }
                ],
                AttributeDefinitions = [
                    {'AttributeName': "programme", 'AttributeType': "S" }
                    ],
                ProvisionedThroughput ={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                
                })

        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print ("table created")
        
        
    table = dynamodb.Table(table_name)    
    for row in rowx:
        programme = row.split(',')[0]
        print(programme)
        code = row.split(',')[1]
        print(code)
        total_seats = row.split(',')[2]
        #print(total_seats)
        gen_seats = row.split(',')[3]
        #print(gen_seats)
        gen_male = row.split(',')[4]
        #print(gen_male)
        gen_female = row.split(',')[5]
        #print(gen_female)
        gen_vacant = row.split(',')[6]
        #print(gen_vacant)
        sc_seats = row.split(',')[7]
        #print(sc_seats)
        sc_male = row.split(',')[8]
        #print(sc_male)
        sc_female = row.split(',')[9]
        #print(sc_female)
        sc_vacant = row.split(',')[10]
        #print(sc_vacant)
        st_seats = row.split(',')[11]
        #print(st_seats)
        st_male = row.split(',')[12]
        #print(st_male)
        st_female = row.split(',')[13]
        #print(st_female)
        st_vacant = row.split(',')[14]
        #print(st_vacant)
        obc_seats = row.split(',')[15]
        #print(obc_seats)
        obc_male = row.split(',')[16]
        #print(obc_male)
        obc_female = row.split(',')[17]
        #print(obc_female)
        obc_vacant = row.split(',')[18]
        #print(obc_vacant)
        pwd_seats = row.split(',')[19]
        #print(pwd_seats)
        pwd_male = row.split(',')[20]
        #print(pwd_male)
        pwd_female = row.split(',')[21]
        #print(pwd_female)
        pwd_vacant = row.split(',')[22]
        #print(pwd_vacant)
        
        table.put_item(
            Item={
                'faculty' : faculty,
                'department' : department,
                'code' : code,
                'programme' : programme,
                'code' : code,
                'total_seats' : total_seats,
                'gen_seats' : gen_seats,
                'gen_male' : gen_male,
                'gen_female' : gen_female,
                'gen_vacant' : gen_vacant,
                'sc_seats' : sc_seats,
                'sc_male' : sc_male,
                'sc_female' : sc_female,
                'sc_vacant' : sc_vacant,
                'st_seats' : st_seats,
                'st_male' : st_male,
                'st_female' : st_female,
                'st_vacant' : st_vacant,
                'obc_seats' : obc_seats,
                'obc_male' : obc_male,
                'obc_female' : obc_female,
                'obc_vacant' : obc_vacant,
                'pwd_seats' : pwd_seats,
                'pwd_male' : pwd_male,
                'pwd_female' : pwd_female,
                'pwd_vacant' : pwd_vacant
                
            }
            )