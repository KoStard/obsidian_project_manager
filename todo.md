Many issues with this implementation
1. sync is breaking current orders
2. lack of autocomplete is a big problem. either add CLI autocomplete or completely move to REPL session for full control
3. add fuzzy search, key navigation
4. windows path separators not working (`\`)
5. fails if there is / in the end of the path