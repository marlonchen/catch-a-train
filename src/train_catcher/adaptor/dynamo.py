import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from types_boto3_dynamodb.service_resource import Table
from typing import Any, Optional
from datetime import datetime


class DynamoTable:
    """
    Adapter class for AWS DynamoDB that encapsulates write and read operations.
    Supports querying by hash key and datetime range for sort key.
    """

    def __init__(self, table_name: str):
        self._table_name = table_name
        self._table: Optional[Table] = None

    def _get_table(self) -> Table:
        if self._table:
            return self._table
        localstack_endpoint = os.getenv('LOCALSTACK_ENDPOINT')
        region = os.getenv('AWS_REGION', 'us-east-1')
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        if localstack_endpoint:
            dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url=localstack_endpoint,
                region_name=region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
        else:
            dynamodb = boto3.resource('dynamodb', region_name=region)
            
        self._table = dynamodb.Table(self._table_name)
        return self._table

        
    def write_item(self, item: dict):
        """
        Write an item to the DynamoDB table.
        
        Args:
            item: Dictionary containing the item attributes
            
        Returns:
            Response from DynamoDB
        """
        response = self._get_table().put_item(Item=item)
        return response
    
    def batch_write_items(self, items: list[dict]) -> dict:
        """
        Write multiple items to the DynamoDB table in a batch.
        
        Args:
            items: List of dictionaries containing item attributes
            
        Returns:
            Response from DynamoDB
        """
        with self._get_table().batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        return {"Status": "Success", "ItemsWritten": len(items)}
    
    def read_item(self, hash_key: str, hash_value: Any) -> dict:
        """
        Read a single item by its hash key.
        
        Args:
            hash_key: The name of the hash/partition key
            hash_value: The value of the hash key
            
        Returns:
            The item if found, otherwise an empty dictionary
        """
        response = self._get_table().get_item(Key={hash_key: hash_value})
        return response.get('Item', {})
    
    def query_by_hash_key(self, hash_key: str, hash_value: Any) -> list[dict]:
        """
        Query items by hash key.
        
        Args:
            hash_key: The name of the hash/partition key
            hash_value: The value of the hash key
            
        Returns:
            List of items matching the hash key
        """
        response = self._get_table().query(
            KeyConditionExpression=Key(hash_key).eq(hash_value)
        )
        return response.get('Items', [])
    
    def query_by_hash_key_and_sort_key_datetime_range(
        self, 
        hash_key: str, 
        hash_value: Any,
        sort_key: str,
        start_datetime: datetime,
        end_datetime: Optional[datetime] = None
    ) -> list[dict]:
        """
        Query items by hash key and a datetime range for the sort key.
        
        Args:
            hash_key: The name of the hash/partition key
            hash_value: The value of the hash key
            sort_key: The name of the sort key (must be a datetime formatted string or number)
            start_datetime: Start of the datetime range
            end_datetime: End of the datetime range (optional, defaults to now if not provided)
            
        Returns:
            List of items matching the query criteria
        """
        # Convert datetime objects to ISO format strings
        start_str = start_datetime.isoformat()
        
        if end_datetime is None:
            end_datetime = datetime.now()
        end_str = end_datetime.isoformat()
        
        # Build the key condition expression
        key_condition = Key(hash_key).eq(hash_value) & \
                        Key(sort_key).between(start_str, end_str)
        
        response = self._get_table().query(
            KeyConditionExpression=key_condition
        )
        return response.get('Items', [])
    