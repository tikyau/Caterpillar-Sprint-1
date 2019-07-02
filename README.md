# Caterpillar-Sprint-1

- I have created Azure tables, Data factory, Batch account and Azure Blob. Created pool with start task steps. 

  The source excel files are stored in blob. I have copied the modified and converted files in Azure Table.
  
  PFA data factory arm template is also included in this repo
  

- Azure Table does not support space in column name. Your excel files have space in column names. E.g. Owner Division. 

  We need to change the destination to Azure SQL DB or we need to assume that there will not be space in excel file.

