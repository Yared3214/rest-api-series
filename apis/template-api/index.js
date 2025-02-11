const express = require("express");
const app = express();
const port = 3000;

app.use(express.json());

app.get("/", (req, res) => {
    res.json({ message: "Welcome to Template API" });
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
