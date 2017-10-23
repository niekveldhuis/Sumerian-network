# Puzriš-Dagan (Drehem) Transaction Types and Commodities

Each edge in our network (a connection between two persons) is found in a document. We can characterize each document by document **type** and use these types as edge attributes. We can create two different attributes: one for *transaction type* and one for *commodity type*. Transaction types may be distinguished by keywords that can be found with simple search. Commodity types are a bit more complex to deal with, we will need to build a classifier.

## Transaction Types (keywords)

The documents arew distinguished from the point of view of the central administration: commodities coming in (deliveries); commodities going out (expenditures); commodities transferred from one office to another (transfers); balanced accounts, and inventories.

### Deliveries

Deliveries are characterized by the keyword **mu-DU** (delivery). The word mu-DU may be followed by a qualification, such as mu-DU lugal (delivery for the king) or mu-kux(DU) {d}szul-gi-si2-im-tum (delivery for [queen] Šulgi-simtum). Often (but not always) the **mu-DU** is followed by the expression **PN i₃-dab₅** (PN took it).

### Expenditures

Expenditures are characterized by the keyword **zi** (to expend) either in the form **PN ba-zi** (PN expended it) or in the form **zi-ga PN** (expenditure of PN). You may also find **zi-ga lugal** (expenditures of the king).

### Transfers

Transfers are characterized by the keyword **dab₅** always in the form **i₃-dab₅**. This same expression is also found in many delivery text, but there it is preceded by **mu-DU**. In transfers the pattern is: 
ki PN-ta      from Mr. X
PN-e i₃-dab₅  Mr. Y took it

### Receipt of dead animals

The specific key word for the transfer of dead animals is **šu ba-ti** (he received).

### Balanced account

Balanced accounts are characterized by **nig₂-ka₉-ak**. This is an account of how many animals a shepherd originally received and how many he still has left.

### Inventory

Inventories are characterized by the phrase **ki-be₂ gi₄-a**. The inventory details how many animals were delivered and how many were expended.

## Types of commodities

The following types of commodities may be distinguished: 
- domestic animals (oxen, cows, sheep, goats, etc.)
- wild animals (bears, gazelles, mountain goats)
- dead animals
- leather objects (boots, sandals, etc.)
- precious objects (objects of copper, bronze, silver and gold, precious stones, etc.)

In order to distinguish between these various types of commodities as edge attributes it may be helpful to collect a good number of such texts and then use a naive Baysian classifier to do the rest,.
