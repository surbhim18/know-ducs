import boto3
import time
#from boto3.dynamodb.conditions import Key, Attr

s3 = boto3.client('s3')
client = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')

def csv_reader(event,context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    obj = s3.get_object(Bucket=bucket,Key=key)
    rows = obj['Body'].read().decode("utf-8").split('\n')
    
    #print(rows)
    
    year = rows[1].split(',')[1]
    
    tableName = "Result_Batch_"+year
    
    # Get an array of table names associated with the current account and endpoint.
    response = client.list_tables()

    if tableName in response['TableNames']:
        table_found = True
    else:
        table_found = False
    
    #dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    
    if table_found == False:
        table = dynamodb.create_table(
            TableName=tableName,
            KeySchema=[
                {
                    'AttributeName': 'semester',
                    'KeyType': 'HASH'  #Partition key
                },
                {
                    'AttributeName': 'roll_no',
                    'KeyType': 'RANGE'  #Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'semester',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'roll_no',
                    'AttributeType': 'S'
                },
        
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
        print("Table status: ", table.table_status)
        # Wait until the table exists
        table.meta.client.get_waiter('table_exists').wait(TableName=tableName)
    
    table = dynamodb.Table(tableName)
    #with table.batch_writer() as batch:
    #print(type(rows))
    
    course = rows[0].split(',')[1]
    semester = rows[2].split(',')[1]
    
    sub = rows[3]
    print(sub)
    
    sub_key_names = []
    sub_key_names.append(sub.split(',')[1])
    #print(sub_key_names)
    
    #count_subs = len(sub.split(','))-1
    #print(count_subs)
    for i in range(2,7):
        sub_key_names.append(sub.split(',')[i]+'_W')
        sub_key_names.append(sub.split(',')[i]+'_IA')
    #print(year)
    print(sub_key_names)
    
    rowx = rows[6:-1]
    #print(rowx)
    
    for row in rowx:
        sub_marks = []
        #print(row)
        
        row_length = len(row.split(','))
        no_of_cols = row_length - 2
        #print("Length",row_length)
        for i in range(2,no_of_cols+1):
            #print("Heyyy column: ",i)
            if row.split(',')[i]=="":
                sub_marks.append("xxxx")
            else:
                sub_marks.append(row.split(',')[i])
        
        #print(sub_marks)
            
        #print("Putting one row into the table...")
        table.put_item(
            Item={
            'semester': semester,
            'roll_no' : row.split(',')[0],
            'course' : course,
            'name' : row.split(',')[1],
             sub_key_names[0] : sub_marks[0],
             sub_key_names[1]: sub_marks[1],
             sub_key_names[2]: sub_marks[2],
             sub_key_names[3]: sub_marks[3],
             sub_key_names[4]:sub_marks[4],
             sub_key_names[5]: sub_marks[5],
             sub_key_names[6]: sub_marks[6],
             sub_key_names[7]: sub_marks[7],
             sub_key_names[8]:sub_marks[8],
             sub_key_names[9]: sub_marks[9],
             sub_key_names[10]: sub_marks[10],
             'total': row.split(',')[13]
            }
        )
    #return True
    
    '''table.put_item(
        Item= {
            'roll_no' : 1,
            'name' : 'bhoomika'
        }
    )'''
    
    '''response = table.query(
        KeyConditionExpression=Key('roll_no').eq('65803')
    )

    item = response['Items']
    print(item)
    name = item[0]['name']
    marks = item[0]['marks']
    print("Hello, {}" .format(name))
    print("Marks obtained are, {}" .format(marks))'''