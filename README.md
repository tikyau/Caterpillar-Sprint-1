# Caterpillar-Sprint-1

- I have created Azure tables, Data factory, Batch account, storage account. Created pool with start task steps. 

  The source excel files are stored in blob. I have copied the modified and converted files in Azure Table.
  
  PFA data factory template code is also included.
  

- Azure Table does not support space in column name. Your excel files have space in column names. E.g. Owner Division. 

  We need to change the destination to Azure SQL DB or we need to assume that there will not be space in excel file.

