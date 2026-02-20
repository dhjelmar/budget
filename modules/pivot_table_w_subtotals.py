def pivot_table_w_subtotals(df, values, indices, columns, aggfunc, fill_value=0):
    """
    Creates a pivot table with dynamic subtotals for each level of indices.
    
    Args:
        df: Input DataFrame
        values: Column(s) to aggregate
        indices: List of columns to group by (hierarchical levels)
        columns: Columns to pivot on
        aggfunc: Aggregation function (e.g., 'sum', 'mean')
        fill_value: Value to fill missing cells
    
    Returns:
        DataFrame with subtotals and grand total
    """
    listOfTable = []
    for i in range(len(indices)):
        n = i + 1
        # Create pivot table with first n levels of indices
        table = pd.pivot_table(
            df, 
            values=values, 
            index=indices[:n], 
            columns=columns, 
            aggfunc=aggfunc, 
            fill_value=fill_value
        ).reset_index()
        
        # Clear higher-level index columns
        for col in indices[n:]:
            table[col] = ''
        
        listOfTable.append(table)
    
    # Concatenate all tables
    concatTable = pd.concat(listOfTable).sort_index()
    concatTable = concatTable.set_index(keys=indices)
    return concatTable.sort_index(axis=0, ascending=True)

# Example usage:
# pivot_table_w_subtotals(df, values='Value', indices=['Store', 'Department', 'Type'], columns=[], aggfunc='sum', fill_value='')   