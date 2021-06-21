
ubc_pm = 'UBC_PM_03_pm10_env'


keep_vars = ['PM1 [ug/m3]', ubc_pm]
df = df_final.drop(columns=[col for col in df_final if col not in keep_vars])
df[ubc_pm+'2'] = df[ubc_pm]
df.tail()

y = df['PM1 [ug/m3]'].values
x = np.stack((df[ubc_pm].values,df[ubc_pm+'2'].values), axis = 1 )

## define a precentage of training data
fracTrain = 0.8 
ntrain = int(np.floor(fracTrain * len(x)))

# subset training  
x_train = x[:ntrain]  
y_train = y[:ntrain]
# subset target
x_test = x[ntrain:]  
y_test = y[ntrain:]



# %%

nhn = 8 
hidden_layers = 2
model = MLPRegressor(
    hidden_layer_sizes=(nhn, hidden_layers),
    verbose=False,
    max_iter=1500,
    early_stopping=True,
    validation_fraction=0.2 ,
    batch_size=32,
    solver="adam" ,
    activation="relu",
    learning_rate_init=0.0001,
)

model.fit(x_train, y_train)  # train the model


y_out_this_nhn = model.predict(
    x
) 



# %%

fig = plt.figure(figsize=(14, 12))
fig.autofmt_xdate()
xfmt = DateFormatter("%m-%d %H:00")
fig.suptitle(r"PM 10 ($\frac{\mu g}{m^3}$)", fontsize=16)
ax = fig.add_subplot(1, 1, 1)
ax.plot(df_final.index,df['PM1 [ug/m3]'].values, lw = 4.0, label = 'GRIMM', color = colors[0])
ax.plot(df_final.index,y_out_this_nhn, label = 'UBC-PM-01 Corrected', color = colors[1])
ax.plot(df_final.index,df[ubc_pm].values, label = 'UBC-PM-01', color = colors[5])
ax.legend()

# %%
fig = plt.figure(figsize=(14, 12))
fig.autofmt_xdate()
xfmt = DateFormatter("%m-%d %H:00")
fig.suptitle(r"PM 1.0 ($\frac{\mu g}{m^3}$)", fontsize=16)
ax = fig.add_subplot(2, 1, 2)
ax.plot(df_final.index,df['PM1 [ug/m3]'].values, lw = 4.0, label = 'GRIMM', color = colors[0])
ax.plot(df_final.index,y_out_this_nhn, label = 'UBC-PM-01 Corrected', color = colors[1])
ax.plot(df_final.index,df[ubc_pm].values, label = 'UBC-PM-01', color = colors[2])
ax.set_ylabel(r'$\frac{\mu g}{m^3}$', rotation=0)
ax.set_xlabel('Time (MM-DD HH)')
ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 2.44),
    ncol=6,
    fancybox=True,
    shadow=True,
)
ax = fig.add_subplot(2, 2, 1)
size = 6
ax.scatter(df_final['PM1 [ug/m3]'], df_final['PM1 [ug/m3]'], s=size, color = colors[0])
ax.scatter(df_final['PM1 [ug/m3]'], y_out_this_nhn, s=size, color = colors[1])
ax.scatter(df_final['PM1 [ug/m3]'], df_final[ubc_pm], s=size, color = colors[2])
ax.set_ylabel(r'$\frac{\mu g}{m^3}$', rotation=0)
ax.set_xlabel(r'$\frac{\mu g}{m^3}$')

ax = fig.add_subplot(2, 2, 2)
bins = 20
alpha = 0.6
ax.hist(df_final['PM1 [ug/m3]'],bins,alpha = alpha, color = colors[0], zorder = 10)
ax.hist(y_out_this_nhn,bins, alpha = alpha, color = colors[1])
ax.hist(df_final[ubc_pm],bins, alpha = alpha, color = colors[2])

ax.set_ylabel('Count')
ax.set_xlabel(r'$\frac{\mu g}{m^3}$')
# %%
