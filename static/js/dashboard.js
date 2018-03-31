//populate select element with possible category values
categoriesUrl = "/fetch_categories";
Plotly.d3.json(categoriesUrl, function (error, response) {
    if (error) console.log(error);
    categoryList = ['All Categories'];
    for (var i = 0; i < response.length; i++) {
        categoryList.push(response[i]);
    }
    //console.log(medalList);
    $categorySelectListMonthStarted = document.getElementById("categorySelectMonthStarted");
    $categorySelectListLengthCampaign = document.getElementById("categorySelectLengthCampaign");
    for (var i = 0; i < categoryList.length; i++) {
        var $optionMonthStarted = document.createElement("option");
        $optionMonthStarted.value = categoryList[i];
        $optionMonthStarted.text = categoryList[i];
        $categorySelectListMonthStarted.appendChild($optionMonthStarted);

        var $optionLengthCampaign = document.createElement("option");
        $optionLengthCampaign.value = categoryList[i];
        $optionLengthCampaign.text = categoryList[i];
        $categorySelectListLengthCampaign.appendChild($optionLengthCampaign);
    }
});