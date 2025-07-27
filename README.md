# expense-tracking


TODO:

### Infra
- [ ] Auth
- [ ] Deployment to cloud run
- [ ] Pairing with Apple Shortcuts

#### User input handling
- [ ] Discover intents: check what user wants to do (photo + prompt) -> to use within receipt handling / expense tracking

#### Receipt handling
- [x] Receipt upload
- [x] Receipt parsing & itemization
- [ ] Receipt storage

#### Expense tracking
- [ ] Expense categorization
- [ ] Assigning people to items (based on input)
- [ ] Saving expense to Splitwise, dividing expense by people (this can be treated as db)
- [ ] Store expense & item in vector db (to check if similar expense was already added / automatically add users to expense) // considered as source of truth, but has to be uploaded the next day or in the night (so that mistakes are not made)

#### Expense visualization
- [ ] Expense overview, based on categories etc. 
